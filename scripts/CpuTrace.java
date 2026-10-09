// Bounded observations from the real Logisim Evolution 3.9.0 simulation engine.
// Exit 0 means trace generation completed, not that the CPU passed its tests.
import com.cburch.logisim.circuit.CircuitState;
import com.cburch.logisim.circuit.SubcircuitFactory;
import com.cburch.logisim.comp.Component;
import com.cburch.logisim.data.Value;
import com.cburch.logisim.file.Loader;
import com.cburch.logisim.instance.Instance;
import com.cburch.logisim.instance.StdAttr;
import com.cburch.logisim.proj.Project;
import com.cburch.logisim.std.memory.Ram;
import com.cburch.logisim.std.memory.Register;
import com.cburch.logisim.std.memory.Rom;
import com.cburch.logisim.std.wiring.Clock;
import com.cburch.logisim.std.wiring.Pin;
import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.StringJoiner;

public class CpuTrace {
    private static CircuitState substate(CircuitState state, String name) {
        for (Component component : state.getCircuit().getNonWires()) {
            if (component.getFactory() instanceof SubcircuitFactory factory
                    && factory.getName().equals(name)) {
                return factory.getSubstate(state, component);
            }
        }
        throw new IllegalArgumentException("Missing subcircuit: " + name);
    }

    private static String registerValues(CircuitState state) {
        var components = new ArrayList<Component>(state.getCircuit().getNonWires());
        components.sort(Comparator.comparingInt(c -> c.getLocation().getY()));
        var result = new StringJoiner(" ");
        for (Component component : components) {
            if (component.getFactory() instanceof Register) {
                var value = state.getInstanceState(component).getPortValue(Register.OUT);
                result.add(component.getLocation() + "=" + value.toHexString());
            }
        }
        return result.toString();
    }

    private static long[] readImage(Path path) throws Exception {
        String[] tokens = Files.readString(path).trim().split("\\s+");
        if (tokens.length < 3 || !tokens[0].equals("v2.0") || !tokens[1].equals("raw")) {
            throw new IllegalArgumentException("Expected the supplied v2.0 raw word image");
        }
        if (tokens.length - 2 > 65536) {
            throw new IllegalArgumentException("Image exceeds the 16-bit address space");
        }
        long[] words = new long[tokens.length - 2];
        for (int i = 2; i < tokens.length; i++) {
            if (!tokens[i].matches("[0-9a-fA-F]{1,4}")) {
                throw new IllegalArgumentException("Invalid 16-bit hex word: " + tokens[i]);
            }
            words[i - 2] = Long.parseLong(tokens[i], 16);
        }
        return words;
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 2 || args.length > 3) {
            throw new IllegalArgumentException("Usage: CpuTrace circuit.circ memory_image.txt [half_ticks]");
        }
        int limit = args.length == 3 ? Integer.parseInt(args[2]) : 120;
        if (limit < 0 || limit > 10000) {
            throw new IllegalArgumentException("half_ticks must be 0..10000");
        }
        long[] words = readImage(Path.of(args[1]));
        var file = new Loader(null).openLogisimFile(new File(args[0]));
        var cpu = file.getMainCircuit();
        boolean foundRom = false;
        Component reset = null;
        Component clock = null;
        for (Component component : cpu.getNonWires()) {
            if (component.getFactory() instanceof Rom) {
                var contents = Rom.getMemContents(Instance.getInstanceFor(component));
                contents.clear();
                contents.set(0, words); // In-memory only; never saves the circuit.
                foundRom = true;
            }
            if (component.getFactory() instanceof Clock) clock = component;
            if (component.getFactory() instanceof Pin
                    && "reset".equals(component.getAttributeSet().getValue(StdAttr.LABEL))) {
                reset = component;
            }
        }
        if (!foundRom || reset == null || clock == null) {
            throw new IllegalArgumentException("Expected this repository's CPU, ROM, reset and clock");
        }
        var project = new Project(file);
        var state = new CircuitState(project, cpu);
        var propagator = state.getPropagator();
        // A separate CircuitState requires explicit dirty notifications for inputs.
        Pin.FACTORY.setValue(state.getInstanceState(reset), Value.TRUE);
        state.markComponentAsDirty(reset);
        propagator.propagate();
        Pin.FACTORY.setValue(state.getInstanceState(reset), Value.FALSE);
        state.markComponentAsDirty(reset);
        propagator.propagate();

        for (int tick = 0; tick <= limit; tick++) {
            System.out.println("TICK " + tick + " PC " + registerValues(substate(state, "PC"))
                    + " REGS " + registerValues(substate(state, "REG_file"))
                    + " OSC " + propagator.isOscillating());
            for (Component component : cpu.getNonWires()) {
                if (component.getFactory() instanceof Ram ram) {
                    var contents = ram.getContents(state.getInstanceState(component));
                    System.out.println("RAM " + contents.get(0) + " " + contents.get(1));
                }
            }
            if (tick < limit) {
                Clock.tick(state, tick + 1, clock);
                state.markComponentAsDirty(clock);
                propagator.propagate();
            }
        }
        System.exit(0); // The simulator's Project owns background service threads.
    }
}
