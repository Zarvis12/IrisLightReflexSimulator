# IrisLightReflexSimulator
A simulation project which simulates Light reflex pathway and it's lesions

# 👁️ Eye Model Simulation: Setup & Usage Guide

This project provides an interactive simulation of the human pupillary light reflex using an Arduino Uno, LDR modules, servos, and LEDs. It features a Python-based Graphical User Interface (GUI) for real-time control and visualization, including the ability to simulate "lesions" in different neural pathways.

---

## 🚀 Project Overview

The core functionalities of this simulation include:

* **Pupillary Light Reflex:** Utilizes two Light Dependent Resistor (LDR) modules to mimic eyes sensing ambient light. Two servo motors then simulate the constriction and dilation of pupils in response to these light changes.
* **Neural Pathway Lesions:** Eight LEDs are integrated to represent key neural pathways involved in the pupillary reflex. These LEDs can be toggled via the Python GUI to visualize an "intact" (LED ON) or "lesioned" (LED OFF) pathway.

---

## 🧠 The Pupillary Light Reflex Explained

The pupillary light reflex is an involuntary neurological response that adjusts the pupil's size based on light intensity, thereby regulating the amount of light reaching the retina. This reflex is vital for protecting the eye from damage due to excessive light and optimizing visual acuity in varying illumination.

It follows a specific neural circuit:

1.  **Afferent Pathway (Sensory Input) ➡️:**
    * Light stimulates photoreceptors in the retina.
    * Sensory signals travel from the retina via the **Optic Nerve (Cranial Nerve II)** of each eye.
    * Fibers from both optic nerves partially cross at the optic chiasm. A subset of these fibers proceeds to the **Pretectal Nucleus** located in the midbrain.

2.  **Interneuron Pathway (Processing) 🔄:**
    * The Pretectal Nucleus processes the light information. Crucially, it sends signals **bilaterally** (to both sides) to the **Edinger-Westphal Nuclei**. This bilateral innervation is fundamental to the **consensual light reflex**, where both pupils constrict even if light is shone into only one eye.

3.  **Efferent Pathway (Motor Output) 🏃‍♂️:**
    * Neurons from the Edinger-Westphal Nuclei then travel along the **Oculomotor Nerve (Cranial Nerve III)**.
    * These parasympathetic fibers synapse in the ciliary ganglion. Post-ganglionic fibers then innervate the *sphincter pupillae muscle*, causing the pupil to **constrict (miosis)**.

---

### 💡 Light Values and Servo (Iris) Response

The simulation maps the LDR module's analog readings (which vary inversely with light intensity) to servo angles, mimicking pupil size.

| LDR Reading Range                                    | Light Intensity | Pupil/Iris State      | Servo Angle (Default) | Effect on Servo    |
| :--------------------------------------------------- | :-------------- | :-------------------- | :-------------------- | :----------------- |
| < `HIGH_INTENSITY_LDR_THRESHOLD` (e.g., < 400)       | High (Bright)   | Constricted (Miosis)  | `HIGH_SERVO_ANGLE` (60°) | Moves to constrict |
| > `LOW_INTENSITY_LDR_THRESHOLD` (e.g., > 600)        | Low (Dim)       | Dilated (Mydriasis)   | `LOW_SERVO_ANGLE` (120°) | Moves to dilate    |
| Between Thresholds                                   | Medium          | Gradually adjusting | Maps linearly         | Smooth transition  |

*Note: The actual servo angles might need slight adjustment based on your physical setup for optimal visual effect.*

---

## 🩹 Lesions and Their Effects

This simulation allows for a conceptual understanding of how damage (lesions) to specific parts of the pupillary light reflex pathway might manifest. While our physical model uses LEDs as visual indicators, in a real biological system, specific effects would be observed:

* **Optic Nerve (CN II) Lesion (Afferent Pathway) 💔:**
    * **Effect:** If, for example, the *left optic nerve* is lesioned, shining a light into the left eye will **not** cause *either* pupil to constrict (neither the left direct nor the right consensual). However, shining light into the *right* (intact) eye **will** cause *both* pupils to constrict normally. This is because the sensory input from the lesioned eye cannot reach the brain, but the motor pathways are fully functional.
    * **Simulation:** Toggling the "Optic Nerve Left/Right" LED off represents a compromised sensory input pathway for that eye.

* **Pretectal Nucleus (PTN) Lesion (Interneuron Pathway) 💔:**
    * **Effect:** Damage to the Pretectal Nucleus can impair or abolish the light reflex, often affecting both direct and consensual responses from the associated eye, depending on the lesion's extent. Severe bilateral damage can lead to pupils that don't react to light but might still react to accommodation (light-near dissociation).
    * **Simulation:** Toggling the "PTN Left/Right" LED off simulates damage to this critical processing center.

* **Edinger-Westphal Nucleus (EWN) Lesion (Efferent Pathway Origin) 💔:**
    * **Effect:** A unilateral lesion (e.g., to the *left* Edinger-Westphal nucleus) would impair constriction of the pupil on the **same side (ipsilateral)**, regardless of which eye is stimulated. The pupil on the *opposite side* (contralateral) would still constrict normally when light is shone into either eye (as its EWN and CN III are intact).
    * **Simulation:** Toggling the "EWP Left/Right" LED off simulates damage to this parasympathetic motor nucleus.

* **Oculomotor Nerve (CN III) Lesion (Efferent Pathway) 💔:**
    * **Effect:** A lesion of the Oculomotor Nerve on one side (e.g., *left* CN III) would cause the left pupil to be **dilated and unreactive** to light (both direct and consensual responses would be absent in the left eye). Shining light into the left eye would still cause the *right* pupil to constrict (intact afferent pathway), but the left pupil would remain dilated due to the efferent pathway damage.
    * **Simulation:** Toggling the "3rd Cranial Nerve Left/Right" LED off simulates damage to the motor nerve directly responsible for pupillary constriction.

**Important Note:** In this specific Arduino implementation, the servo-based pupillary reflex is *directly controlled by the LDR readings* and **does not dynamically change based on the LED lesion states**. The LEDs serve as visual indicators to help you conceptually map where a lesion might occur in the pathway. For a truly interactive lesion simulation on the pupil size, the Arduino code would need to be modified to integrate the LED states into the servo control logic.

### 🔦 Relative Afferent Pupillary Defect (RAPD)

A **Relative Afferent Pupillary Defect (RAPD)**, also known as a Marcus Gunn pupil, is a neurological sign indicating a lesion in the afferent pathway (optic nerve or severe retinal disease) of one eye. It's often detected using the "swinging flashlight test":

* **Test:** When a light is swung from the unaffected eye to the affected eye, the affected pupil paradoxically *dilates* instead of constricting, even though both pupils should be constricting to light. When the light is swung back to the unaffected eye, both pupils constrict again.
* **Cause:** The damaged optic nerve in the affected eye transmits a weaker light signal to the brain compared to the healthy eye. This causes a lesser degree of pupillary constriction when light hits the affected eye, effectively making it seem like the light source is dimmer than it actually is.
* **How this simulation relates:** While this simulation does not perform a "swinging flashlight test" with the servos directly responding to it, **conceptually, turning OFF the "Optic Nerve Left" or "Optic Nerve Right" LED in the GUI indicates the presence of an afferent defect** on that side. This LED allows you to visually represent the damaged pathway that would lead to an RAPD in a real patient.

### 🧪 Lesion Permutations for Testing

This table outlines various lesion scenarios you can simulate using the Python GUI's LED controls. Remember, the LEDs are indicators; the servo's physical response is based on LDR readings.

| Scenario                                        | Affected Pathway(s) (LED to turn OFF in GUI)                      | Real-World Expected Pupillary Response (Direct/Consensual when light in eye)                                                                      | Simulation Visual Indicator (LED State)      |
| :---------------------------------------------- | :---------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------- |
| **1. Normal Reflex** | All LEDs ON                                                       | **Light in Left Eye:** Left pupil constricts (direct), Right pupil constricts (consensual).<br>**Light in Right Eye:** Right pupil constricts (direct), Left pupil constricts (consensual). | All LEDs GREEN (ON)                          |
| **2. Left Optic Nerve Lesion** | `Optic Nerve Left` OFF                                            | **Light in Left Eye:** Neither pupil constricts (no afferent signal from left).<br>**Light in Right Eye:** Both pupils constrict normally.        | `Optic Nerve Left` RED (OFF), others GREEN (ON) |
| **3. Right Optic Nerve Lesion** | `Optic Nerve Right` OFF                                           | **Light in Right Eye:** Neither pupil constricts (no afferent signal from right).<br>**Light in Left Eye:** Both pupils constrict normally.         | `Optic Nerve Right` RED (OFF), others GREEN (ON) |
| **4. Left 3rd Cranial Nerve (CN III) Lesion** | `3rd Cranial Nerve Left` OFF                                      | **Light in Left Eye:** Left pupil remains dilated (no efferent), Right pupil constricts (consensual intact).<br>**Light in Right Eye:** Left pupil remains dilated (no efferent), Right pupil constricts (direct intact). | `3rd Cranial Nerve Left` RED (OFF), others GREEN (ON) |
| **5. Right 3rd Cranial Nerve (CN III) Lesion** | `3rd Cranial Nerve Right` OFF                                     | **Light in Right Eye:** Right pupil remains dilated (no efferent), Left pupil constricts (consensual intact).<br>**Light in Left Eye:** Right pupil remains dilated (no efferent), Left pupil constricts (direct intact). | `3rd Cranial Nerve Right` RED (OFF), others GREEN (ON) |
| **6. Left Edinger-Westphal Nucleus (EWN) Lesion** | `Edinger-Westphal Nucleus Left` OFF                             | **Light in Left Eye:** Left pupil remains dilated (no efferent from EWN), Right pupil constricts (consensual intact).<br>**Light in Right Eye:** Left pupil remains dilated (no efferent from EWN), Right pupil constricts (direct intact). | `Edinger-Westphal Nucleus Left` RED (OFF), others GREEN (ON) |
| **7. Right Edinger-Westphal Nucleus (EWN) Lesion** | `Edinger-Westphal Nucleus Right` OFF                            | **Light in Right Eye:** Right pupil remains dilated (no efferent from EWN), Left pupil constricts (consensual intact).<br>**Light in Left Eye:** Right pupil remains dilated (no efferent from EWN), Left pupil constricts (direct intact). | `Edinger-Westphal Nucleus Right` RED (OFF), others GREEN (ON) |
| **8. Bilateral Optic Nerve Lesion** | `Optic Nerve Left` OFF, `Optic Nerve Right` OFF                   | **Light in Left Eye:** Neither pupil constricts.<br>**Light in Right Eye:** Neither pupil constricts. (No afferent signals reaching brain).        | Both `Optic Nerve` LEDs RED (OFF)            |
| **9. Bilateral 3rd Cranial Nerve (CN III) Lesion** | `3rd Cranial Nerve Left` OFF, `3rd Cranial Nerve Right` OFF       | **Light in Any Eye:** Both pupils remain dilated (no efferent response).                                                                           | Both `3rd Cranial Nerve` LEDs RED (OFF)      |
| **10. Left PTN Lesion** | `Pretectal Nucleus Left` OFF                                      | **Light in Left Eye:** Impaired or absent direct/consensual response (depends on exact lesion location).<br>**Light in Right Eye:** Normal direct/consensual response (generally). | `Pretectal Nucleus Left` RED (OFF), others GREEN (ON) |

---

## 🛠️ Prerequisites

Before diving in, ensure you have a basic familiarity with:

* **Arduino IDE:** Understanding how to upload code to an Arduino board.
* **Python:** Basic knowledge of running Python scripts from a terminal.
* **Electronics Fundamentals:** Familiarity with breadboards, resistors, LEDs, LDR modules, and servo motors.

---

## 📦 Hardware Requirements

To build and run this project physically, you'll need the following components:

* **Arduino Board:** 1x **Arduino Uno**
* **Breadboards:** 2x Half-size breadboards (as depicted in `diagram.json`).
* **Servo Motors:** 2x SG90 (or similar small) servo motors.
* **LDR Modules:** 2x LDR modules. These usually come as small PCBs with the LDR and necessary resistors integrated, providing a direct analog output pin.
* **LEDs:** 8x LEDs (using various colors, as seen in `diagram.json`, can help differentiate pathways).
* **Resistors:** 8x 220Ω or 330Ω resistors (for current limiting with LEDs).
* **Jumper Wires:** An assortment of male-to-male jumper wires for connections.
* **USB Cable:** 1x Type A to Type B USB cable (for Arduino Uno connection).

---

## 💻 Software Requirements

* **Arduino IDE:** Download and install the latest version from [arduino.cc/en/software](https://www.arduino.cc/en/software).
* **Python 3:** Download and install Python 3 (latest stable version recommended) from [python.org/downloads](https://www.python.org/downloads/). During installation, it's highly recommended to check the "Add Python to PATH" option for easier command-line access.
* **Python Libraries:** The Python GUI relies on the `pyserial` library for communication with the Arduino.

    To install `pyserial`, open your terminal or command prompt and run:

    ```bash
    pip install pyserial
    ```

---

## 🔌 Circuit Assembly: Detailed Wiring Guide

The `diagram.json` file can be opened directly in [Wokwi](https://www.wokwi.com/) to interactively visualize the circuit. You can also view the circuit and its connections interactively on Wokwi: [https://wokwi.com/projects/435562967034133505](https://wokwi.com/projects/435562967034133505)

**Always ensure your Arduino is disconnected from power before making any wiring changes!**

### General Wiring Principles:

* **Power (5V) & Ground (GND):** Always connect the positive power pins (VCC) of your components to the Arduino's `5V` pin and the ground pins (GND) to the Arduino's `GND` pins. It's good practice to use the power rails on your breadboards to distribute 5V and GND efficiently.

### Specific Jumper Wire Connections:

#### 1. LDR Modules:

Each LDR module typically has `VCC`, `GND`, and `AO` (Analog Output) pins.

* **LDR Module 1 (Left Eye):**
    * Connect `VCC` pin to Arduino `5V`.
    * Connect `GND` pin to Arduino `GND`.
    * Connect `AO` pin to Arduino **Analog Pin A0**.
* **LDR Module 2 (Right Eye):**
    * Connect `VCC` pin to Arduino `5V`.
    * Connect `GND` pin to Arduino `GND`.
    * Connect `AO` pin to Arduino **Analog Pin A1**.

#### 2. Servos (SG90):

SG90 servos usually have three wires: Brown (GND), Red (VCC), and Orange (Signal).

* **Servo 1 (Left Pupil):**
    * Connect **Brown (GND) wire** to Arduino `GND`.
    * Connect **Red (VCC) wire** to Arduino `5V`.
    * Connect **Orange (Signal) wire** to Arduino **Digital Pin 9**.
* **Servo 2 (Right Pupil):**
    * Connect **Brown (GND) wire** to Arduino `GND`.
    * Connect **Red (VCC) wire** to Arduino `5V`.
    * Connect **Orange (Signal) wire** to Arduino **Digital Pin 10**.

#### 3. LEDs (Lesion Pathway Indicators):

Each LED needs a current-limiting resistor (220Ω or 330Ω) in series. Remember that the **longer leg of an LED is the anode (+)** and the **shorter leg is the cathode (-)**.

* For **each of the 8 LEDs**:
    1.  Connect one leg of a **220Ω or 330Ω resistor** to the specified Arduino Digital Pin.
    2.  Connect the **anode (longer leg)** of the LED to the **other leg of the resistor**.
    3.  Connect the **cathode (shorter leg)** of the LED to Arduino `GND`.

* **Specific LED Pin Assignments (from `Light_Reflex_Simulator.ino`):**
    * **Optic Nerve Left LED:** Connect to Arduino **Digital Pin 2**.
    * **Optic Nerve Right LED:** Connect to Arduino **Digital Pin 3**.
    * **Pretectal Nucleus Left LED:** Connect to Arduino **Digital Pin 4**.
    * **Pretectal Nucleus Right LED:** Connect to Arduino **Digital Pin 5**.
    * **Edinger-Westphal Nucleus Left LED:** Connect to Arduino **Digital Pin 6**.
    * **Edinger-Westphal Nucleus Right LED:** Connect to Arduino **Digital Pin 7**.
    * **3rd Cranial Nerve Left LED:** Connect to Arduino **Digital Pin 8**.
    * **3rd Cranial Nerve Right LED:** Connect to Arduino **Digital Pin 11**.

---

## ✍️ Arduino Code Setup

1.  **Open Arduino IDE:** Launch your Arduino IDE.
2.  **Open the Sketch:** Go to `File > Open` and navigate to the `Light_Reflex_Simulator.ino` file.
3.  **Select Board & Port:**
    * Navigate to `Tools > Board > Arduino AVR Boards` and select "**Arduino Uno**".
    * Go to `Tools > Port` and select the serial port that corresponds to your connected Arduino Uno.
4.  **Upload the Code:** Click the "Upload" button (the right arrow icon ▶️) in the Arduino IDE toolbar to compile and upload the sketch to your Arduino board.

### Arduino Code (`Light_Reflex_Simulator.ino`) Notes:

* **Pin Definitions:** The code clearly defines pins for LDRs, Servos, and Lesion LEDs.
* **LDR Thresholds:** `HIGH_INTENSITY_LDR_THRESHOLD` and `LOW_INTENSITY_LDR_THRESHOLD` define the light levels for pupil constriction/dilation. These are the default values and can be adjusted dynamically via the Python GUI.
    * *Important:* LDR module values are typically inversely proportional to light intensity (lower analog reading in bright light, higher analog reading in dim light). The code is set up for this common behavior, where a **low** LDR analog value means **high** light intensity.
* **Servo Control:** The `map` function is used to map LDR readings to servo angles, simulating pupil size.
* **Serial Communication:** The Arduino communicates with the Python GUI via serial. It listens for commands like `SET_LDR_THRESH:<high>,<low>` and `SET_PIN_STATE:<pinNum>,<state>`.
* **Lesion Logic:** `digitalWrite(pinNum, (state == 1) ? HIGH : LOW);`
    * `HIGH` (state 1) means the LED is ON, simulating an **INTACT** pathway.
    * `LOW` (state 0) means the LED is OFF, simulating a **LESIONED** pathway.

---

## 🖥️ Python GUI Setup & Usage

1.  **Save the Python File:** Ensure the `Build control.py` file is saved in a convenient directory on your computer.
2.  **Run the GUI:** Open your terminal or command prompt. Navigate to the directory where you saved `Build control.py`. Then, execute the script using Python:

    ```bash
    python "Build control.py"
    ```

### Python GUI Features:

* **Serial Connection:** The GUI automatically lists available serial ports. Select your Arduino's port from the dropdown menu and click **"Connect to Arduino"**.
* **LDR Thresholds:**
    * You can adjust `High Intensity Threshold` and `Low Intensity Threshold` using sliders.
    * `High Intensity Threshold`: When LDR readings are **below** this value, it's interpreted as bright light (pupil constricts).
    * `Low Intensity Threshold`: When LDR readings are **above** this value, it's interpreted as dim light (pupil dilates).
    * **Important Logic:** The GUI enforces that `High Intensity Threshold` must be **less than** `Low Intensity Threshold`. This is vital for correct LDR behavior because LDR analog values typically *decrease* as light intensity *increases*.
* **Lesion Control:** Toggle buttons are provided for each neural pathway (Optic Nerve, Pretectal Nucleus, Edinger-Westphal Nucleus, 3rd Cranial Nerve) for both left and right sides.
    * **Green Button:** Indicates the pathway is **INTACT** (corresponding LED is ON).
    * **Red Button:** Indicates the pathway is **LESIONED** (corresponding LED is OFF).
* **Real-time LDR Readings:** The GUI continuously displays live LDR readings from both the left and right "eyes," providing immediate feedback on perceived light intensity.

---

## ✅ Testing the System

Follow these steps to test your assembled eye model simulation:

1.  **Hardware Connection:** Ensure your Arduino Uno is connected to your computer via USB, and all components are wired correctly as per the `Circuit Assembly` section.
2.  **Arduino Code Upload:** Ensure the `Light_Reflex_Simulator.ino` sketch has been successfully uploaded to your Arduino Uno.
3.  **Run Python GUI:** Execute the `Build control.py` script from your terminal.
4.  **Connect in GUI:** In the Python GUI, select the correct COM port for your Arduino and click **"Connect to Arduino"**.
5.  **Test LDRs and Servos (Pupillary Light Reflex):**
    * Observe the "Current LDR Readings" in the GUI.
    * **Simulate Bright Light:** Shine a flashlight or phone light directly onto an LDR module. You should see its LDR reading decrease, and the corresponding servo motor should rotate, simulating **pupil constriction**.
    * **Simulate Dim Light/Darkness:** Cover an LDR module with your hand. Its LDR reading should increase, and the servo should rotate to a different position, simulating **pupil dilation**.
    * Experiment with adjusting the "High Intensity Threshold" and "Low Intensity Threshold" sliders in the GUI. Click **"Set LDR Thresholds"** after making changes to see how it affects the servo's responsiveness to light.
6.  **Test Lesion Switches (LEDs):**
    * Click on the toggle buttons for each neural pathway in the GUI (e.g., "Optic Nerve Left").
    * Observe the corresponding physical LED connected to your Arduino.
        * When the button in the GUI is **Green (INTACT)**, the LED should be **ON**.
        * When the button in the GUI is **Red (LESION)**, the LED should be **OFF**.
    * *(Reminder: The LEDs visually indicate the lesion state, but the servo movement itself is not directly affected by these lesion states in this version of the code.)*

---

## 🛑 Troubleshooting Common Errors

Here are frequent issues and their solutions to help you get your eye model simulation running smoothly:

### 1. "Connection Required" Warning (Python GUI)

* **Problem:** The Python GUI cannot establish serial communication with the Arduino.
* **Solutions:**
    * 🔌 **Check Arduino Connection:** Is your Arduino Uno physically plugged into your computer via a USB cable?
    * 🔢 **Verify COM Port:** In the Python GUI, ensure you've selected the *correct* COM port from the dropdown. You can typically find your Arduino's COM port listed in the Arduino IDE under `Tools > Port`.
    * 🚫 **Port In Use:** Close any other applications that might be using the serial port (e.g., Arduino Serial Monitor, other Python scripts). Only one application can access a serial port at a time.
    * ⚡ **Arduino Powered?**: Is your Arduino receiving power? The USB connection usually provides this.
    * 🔄 **Restart Everything:** Sometimes, simply closing both the Python GUI and the Arduino IDE, then reopening them and trying to connect again, can resolve transient issues.

### 2. Arduino Upload Fails ("Error compiling for board...", "Port not found", etc.)

* **Problem:** The Arduino IDE cannot compile or upload the sketch to the board.
* **Solutions:**
    * ⚙️ **Correct Board Selected:** In the Arduino IDE, go to `Tools > Board > Arduino AVR Boards` and confirm that "**Arduino Uno**" is selected.
    * 🔌 **Correct Port Selected:** In the Arduino IDE, go to `Tools > Port` and ensure the specific serial port for your Arduino is selected.
    * ↔️ **USB Cable Issues:** Try using a different USB cable. Some cables are "charge-only" and do not support data transmission.
    * ➡️ **Driver Issues:** Ensure the necessary Arduino USB drivers are installed on your operating system. They usually install automatically with the Arduino IDE.
    * ❌ **Python GUI Running:** Make sure the Python GUI is **closed** before attempting to upload new code to the Arduino. The GUI will occupy the serial port, preventing the Arduino IDE from using it.

### 3. Servos Not Moving or Moving Erratically

* **Problem:** The servo motors are not responding as expected to light changes.
* **Solutions:**
    * 🔗 **Double-Check Servo Wiring:** Carefully verify that the Brown (GND), Red (VCC), and Orange (Signal) wires of each servo are connected to the correct pins on your Arduino (GND, 5V, and Digital Pins 9/10 respectively).
    * 🔋 **Power Sufficiency:** While small SG90 servos generally draw low current, ensure your Arduino is receiving stable power, typically from the USB connection. If you have many components or very long wires, power issues can arise.
    * 💡 **LDR Module Wiring:** Confirm that your LDR modules are correctly wired (VCC, GND, and AO connected to 5V, GND, and Analog Pins A0/A1 respectively).
    * 📊 **Monitor LDR Readings:** Observe the "Current LDR Readings" in the Python GUI.
        * If they are stuck (e.g., always 0 or 1023) or not changing when light changes, there's likely a wiring issue with the LDR module, or the module itself might be faulty.
        * If the readings *are* changing but the servos don't react as expected, proceed to the next step.
    * 📈 **Adjust LDR Thresholds:** Fine-tune the `High Intensity Threshold` and `Low Intensity Threshold` values in the Python GUI. Remember that LDR values generally *decrease* in brighter light and *increase* in darker light. Ensure your thresholds are set appropriately for your ambient light conditions and LDR sensitivity.
    * 🚫 **Physical Obstruction:** Make sure the servo arms are not physically blocked by anything, which could prevent them from moving freely.

### 4. LEDs Not Lighting Up (Lesion Indicators)

* **Problem:** The LEDs representing the neural pathways are not illuminating.
* **Solutions:**
    * ➕➖ **LED Polarity:** LEDs are diodes; current flows in only one direction. The **longer leg (anode)** must be connected towards the positive (resistor/Arduino pin), and the **shorter leg (cathode)** towards ground.
    * ⚡ **Current-Limiting Resistor:** Ensure you have a **220Ω or 330Ω resistor** in series with *each* LED. Connecting an LED directly to 5V without a resistor will quickly burn out the LED or potentially damage the Arduino pin.
    * 📌 **Correct Arduino Pins:** Double-check that each LED (via its resistor) is connected to the specific Arduino Digital Pin as specified in the `Circuit Assembly` section (e.g., Optic Nerve Left LED to Pin 2).
    * 🟢 **GUI Toggle State:** Verify that the corresponding toggle button in the Python GUI is set to **Green (INTACT)**. When the button is red, the LED is intentionally turned off to simulate a lesion.

### 5. "High Intensity Threshold must be less than Low Intensity Threshold" Warning (Python GUI)

* **Problem:** This warning appears in the Python GUI when you try to set the LDR thresholds incorrectly.
* **Solution:** This is a crucial logical check implemented in the Python GUI. For most LDR modules, as light intensity *increases*, their analog reading (resistance) *decreases*. Therefore:
    * The LDR value representing "high intensity" (bright light) will be a **smaller number**.
    * The LDR value representing "low intensity" (dim light) will be a **larger number**.
    * **Always ensure the numerical value you set for `High Intensity Threshold` is *smaller than* the numerical value for `Low Intensity Threshold`.** Adjust the sliders accordingly. For example, `High Intensity: 300`, `Low Intensity: 700` is a valid and common configuration.

### 6. Python Commands Not Recognized (e.g., `python is not recognized as an internal or external command`)

* **Problem:** Your operating system cannot find the Python executable when you type `python` or `pip` in the terminal. This means Python is not correctly added to your system's PATH environment variable.
* **Solutions:**
    * **Windows:**
        * If you did not check "Add Python to PATH" during installation, you will need to add it manually.
        * Search for "Environment Variables" in the Windows search bar and select "Edit the system environment variables."
        * Click "Environment Variables..."
        * Under "System variables," find the `Path` variable and select "Edit."
        * Click "New" and add the paths to your Python installation directory (e.g., `C:\Python39\` and `C:\Python39\Scripts\`). Replace `Python39` with your installed version (e.g., `Python310` for Python 3.10).
        * Click "OK" on all windows to save changes. You **must** restart your command prompt/terminal for changes to take effect.
    * **macOS and Linux:**
        * Python is often pre-installed or package managers (like Homebrew on macOS, `apt` on Debian/Ubuntu, `yum` on Fedora/RHEL) handle PATH automatically.
        * If you installed Python manually or to a custom location, you might need to add it to your shell's configuration file (`.bashrc`, `.zshrc`, `.bash_profile` in your home directory).
        * Open your terminal and type `nano ~/.bashrc` (or `~/.zshrc` for zsh, or `~/.bash_profile` for bash login shells).
        * Add a line like: `export PATH="/path/to/python_install/bin:$PATH"` (replace `/path/to/python_install/bin` with the actual directory containing your `python` and `pip` executables).
        * Save the file (Ctrl+O, Enter) and exit (Ctrl+X).
        * Apply the changes by running `source ~/.bashrc` (or your respective file) or by restarting your terminal.

---

By systematically following this guide and troubleshooting common issues, you should be able to successfully set up, run, and experiment with your eye model simulation!

