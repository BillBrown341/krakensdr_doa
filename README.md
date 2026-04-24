# Kraken SDR DoA DSP
This software is intended to demonstrate the direction of arrival (DoA) estimation capabilities of the KrakenSDR and other RTL-SDR based coherent receiver systems which use the compatible data acquisition system - HeIMDALL DAQ Firmware.

The complete application is broken down into two main modules in terms of implementation, into the DAQ Subsystem and to the DSP Subsystem. These two modules can operate together either remotely through Ethernet connection or locally on the same host using shared-memory.

Running these two subsystems on separate processing units can grant higher throughput and stability, while running on the same processing unit makes the entire system more compact.

## Full Instructions
Please [consult the Wiki on the kraken_docs repo](https://github.com/krakenrf/krakensdr_docs/wiki) for full documentation on the use of the KrakenSDR.

## Raspberry Pi 4/5 and Orange Pi 5B Image QUICKSTART

**Download Latest Images From :** https://www.dropbox.com/scl/fo/uf6uosh31syxwt8m32pl4/ANeDj_epfa_PRliPPqCDSoU?rlkey=ovo459p6aiwio785d0h56lj7h&e=1&dl=0

**Alternative Download:** https://drive.google.com/drive/folders/14NuCOGM1Fh1QypDNMngXEepKYRBsG--B?usp=sharing

In these image the code will automatically run on boot. Note that it may take 2-3 minutes for the boot process to complete. 

To run this code flash the image file to an SD Card using Etcher. The SD Card needs to be at least 8GB and we recommend using a class 10 card or faster. For advanced users the login/password details for SSH and terminal are "krakenrf"/"krakensdr"

Note that for the Orange Pi 5B, the image is for the Orange Pi 5**B** specifically. This is the Orange Pi 5 model with the included WiFi module.

Please follow the rest of the guide at https://github.com/krakenrf/krakensdr_docs/wiki/02.-Direction-Finding-Quickstart-Guide
    
### Pi 4 Overclock
To get the best performance we recommend adding aftermarket cooling to your Pi 4 and overclocking to at least 2000 MHz. We won't provide instructions for overclocking here, but they can be easily Googled.
    
### KerberosSDR Setup (KrakenSDR users Ignore)

Consult the Wiki page at https://github.com/krakenrf/krakensdr_docs/wiki/10.-KerberosSDR-Setup-for-KrakenSDR-Software for information on setting up your KerberosSDR to work with the KrakenSDR software.

## Software Quick Start

1) The code will automatically begin processing on boot, please wait for it to start. If started the "Frame Index" will be incrementing.
2) Enter your desired center frequency and click on "Update Receiver Parameters" to tune and calibrate on that frequency.
3) Enter your antenna array configuration details in the "DoA Configuration" card.
4) Set the VFO-0 bandwidth to the bandwidth of your signal.
5) Open the "Spectrum" button and ensure that your signal of interest is active and selected by the VFO-0 window. If it is a bursty signal, determine an appropriate squelching power, and enter it back into the VFO-0 squelch settings in the confuration screen.
6) Open the DOA Estimation tab to see DOA info.
7) Connect to the Android App for map visualization (See Android Instructions - coming later)

You can also 'click to tune' in the spectrum. Either by clicking on the spectrum graph or the waterfall at the frequency of interest.

## VirtualBox Image
If you do not wish to use a Pi 4 as your KrakenSDR computing device, you can also use a Windows or Linux Laptop/PC with our VirtualBox pre-made image. This image file is currently in beta. It includes the KrakenSDR DOA, Passive Radar, and GNU Radio software.

See our Wiki for more information about our VirtualBox Image and where to download it https://github.com/krakenrf/krakensdr_docs/wiki/09.-VirtualBox,-Docker-Images-and-Install-Scripts#virtualbox

## Docker Image

See our Wiki for more information about the third party Docker image https://github.com/krakenrf/krakensdr_docs/wiki/09.-VirtualBox,-Docker-Images-and-Install-Scripts#docker

## Manual Installation from a fresh OS

### Install script

You can use on of our install scripts to automate a manual install. Details on the Wiki at https://github.com/krakenrf/krakensdr_docs/wiki/09.-VirtualBox,-Docker-Images-and-Install-Scripts#install-scripts

###  Manual Install

Manual install is only required if you are not using the premade images, and are setting up the software from a clean system.

1. Install the prerequisites

``` bash
sudo apt -y update
sudo apt -y install nodejs jq rustc cargo php-cli
cargo install miniserve
```

(**OPTIONAL** - rustc, cargo and miniserver are not needed for 99% of users, and we don't recommend installing unless you know what you're doing)

(NOTE: If installing miniserve you might need to get the latest rustc directly from Rust depending on your OS - see Issue https://github.com/krakenrf/krakensdr_doa/issues/131)
```bash
sudo apt -y install rustc cargo
cargo install miniserve
```

2. Install Heimdall DAQ

If not done already, first, follow the instructions at https://github.com/krakenrf/heimdall_daq_fw/tree/main to install the Heimdall DAQ Firmware.

3. Set up Miniconda environment

You will have created a Miniconda environment during the Heimdall DAQ install phase.

Please run the installs in this order as we need to ensure a specific version of dash and Werkzeug is installed because newer versions break compatibility with other libraries.

``` bash
conda activate kraken

conda install pandas
conda install orjson
conda install matplotlib
conda install requests

pip3 install dash_bootstrap_components==1.1.0
pip3 install quart_compress==0.2.1
pip3 install quart==0.17.0
pip3 install dash_devices==0.1.3
pip3 install pyargus

conda install dash==1.20.0
conda install werkzeug==2.0.2
conda install -y plotly==5.23.0
```

4. (**OPTIONAL**) Install GPSD if you want to run a USB GPS on the Pi 4. 

```
sudo apt install gpsd
pip3 install gpsd-py3
```

5. Install the `krakensdr_doa` software

```bash
cd ~/krakensdr
git clone https://github.com/krakenrf/krakensdr_doa
```

Copy the the `krakensdr_doa/util/kraken_doa_start.sh` and the `krakensdr_doa/util/kraken_doa_stop.sh` scripts into the krakensdr root folder of the project.
```bash
cp krakensdr_doa/util/kraken_doa_start.sh .
cp krakensdr_doa/util/kraken_doa_stop.sh .
```

## Running

### Local operation (Recommended)

```bash
./kraken_doa_start.sh
```

Please be patient on the first run, as it can take 1-2 minutes for the JIT numba compiler to compile the numba optimized functions (on Pi 4 hardware), and during this compilation time it may appear that the software has gotten stuck. On subsqeuent runs this loading time will be much faster as it will read from cache.

### Remote operation

With remote operation you can run the DAQ on one machine on your network, and the DSP software on another. 

1. Start the heimdall DAQ subsystem on your remote computing device. (Make sure that the `daq_chain_config.ini` contains the proper configuration) 
    (See:https://github.com/krakenrf/heimdall_daq_fw/blob/main/Documentation/HDAQ_firmware_ver1.0.20201130.pdf)
2. Set the IP address of the DAQ Subsystem in the `settings.json`, `default_ip` field.
3. Start the DoA DSP software by typing:
`./gui_run.sh`
4. To stop the server and the DSP processing chain run the following script:
`./kill.sh`

After starting the script a web based server opens at port number `8080`, which then can be accessed by typing `KRAKEN_IP:8080/` in the address bar of any web browser. You can find the IP address of the KrakenSDR Pi4 wither via your routers WiFi management page, or by typing `ip addr` into the terminal. You can also use the hostname of the Pi4 in place of the IP address, but this only works on local networks, and not the internet, or mobile hotspot networks.

![image](https://user-images.githubusercontent.com/78108016/175924475-2ce0a189-e119-4442-8893-0d32404847e2.png)


### Headless Mode

The application can run entirely without the web GUI. In headless mode the Dash server (port 8080) and file server (port 8081) are not started — the WebSocket on port 8082 is the sole interface for both receiving data and sending commands.

```bash
./gui_run.sh --headless
```

Data streams and commands work identically to GUI mode. The GUI can still be opened later by restarting without `--headless`.

### WebSocket Interface

All data output and remote control is available via a single WebSocket endpoint:

```
ws://KRAKEN_IP:8082/ws/kraken
```

No authentication is required. On connect, the server immediately pushes the current settings snapshot.

#### Outbound messages (server → client)

Every message is a JSON object with a `type` field and a `timestamp` (epoch milliseconds):

```
{ "type": "settings", "timestamp": 1714000000000, "center_freq": 416.588, ... }
{ "type": "doa",      "timestamp": 1714000000000, "doa_max": 135.0, ... }
{ "type": "spectrum", "timestamp": 1714000000000, "freq_axis": [...], "channels": { "ch0": [...] } }
```

#### Inbound commands (client → server)

Send a JSON object to update any combination of settings. Only the keys you include are changed — the rest are preserved.

```json
{
  "type": "command",
  "action": "update_settings",
  "data": {
    "center_freq": 433.92,
    "uniform_gain": 20.0
  }
}
```

Changes apply immediately to the signal processor. If the GUI is open, all form fields update automatically within one second.

#### Settings reference

| Key | Type | Valid values / range | Default |
|-----|------|----------------------|---------|
| `center_freq` | float (MHz) | ≥ 24.0 | `416.588` |
| `uniform_gain` | float (dB) or string | `0, 0.9, 1.4, 2.7, 3.7, 7.7, 8.7, 12.5, 14.4, 15.7, 16.6, 19.7, 20.7, 22.9, 25.4, 28.0, 29.7, 32.8, 33.8, 36.4, 37.2, 38.6, 40.2, 42.1, 43.4, 43.9, 44.5, 48.0, 49.6` or `"Auto"` | `15.7` |
| `data_interface` | string | `"shmem"`, `"eth"` | `"shmem"` |
| `default_ip` | string | Any IP address | `"0.0.0.0"` |
| **DoA** | | | |
| `en_doa` | bool | `true`, `false` | `true` |
| `ant_arrangement` | string | `"UCA"`, `"ULA"`, `"Custom"` | `"UCA"` |
| `ula_direction` | string | `"Both"`, `"Forward"`, `"Backward"` | `"Both"` |
| `ant_spacing_meters` | float (m) | ≥ 0.001 | `0.21` |
| `custom_array_x_meters` | string | Comma-separated floats, one per channel | `"0.21,0.06,-0.17,-0.17,0.07"` |
| `custom_array_y_meters` | string | Comma-separated floats, one per channel | `"0.00,-0.20,-0.12,0.12,0.20"` |
| `array_offset` | int (degrees) | Any integer | `0` |
| `doa_method` | string | `"Bartlett"`, `"Capon"`, `"MEM"`, `"TNA"`, `"MUSIC"`, `"ROOT-MUSIC"` | `"MUSIC"` |
| `doa_decorrelation_method` | string | `"Off"`, `"FBA"`, `"TOEP"`, `"FBSS"`, `"FBTOEP"` | `"Off"` |
| `expected_num_of_sources` | int | `1`, `2`, `3`, `4` | `1` |
| `compass_offset` | int (degrees) | Any integer | `0` |
| `doa_fig_type` | string | `"Linear"`, `"Polar"`, `"Compass"` | `"Linear"` |
| `en_peak_hold` | bool | `true`, `false` | `false` |
| **Station** | | | |
| `station_id` | string | Any string | `"NOCALL"` |
| `location_source` | string | `"None"`, `"Static"`, `"gpsd"` | `"None"` |
| `latitude` | float | -90.0 to 90.0 | `0.0` |
| `longitude` | float | -180.0 to 180.0 | `0.0` |
| `heading` | float (degrees) | 0.0 to 360.0 | `0.0` |
| `gps_fixed_heading` | bool | `true`, `false` | `false` |
| `gps_min_speed` | float (m/s) | > 0 | `2` |
| `gps_min_speed_duration` | int (s) | > 0 | `3` |
| `doa_data_format` | string | `"Kraken App"`, `"Kraken Pro Local"`, `"Kraken Pro Remote"`, `"Kerberos App"`, `"DF Aggregator"`, `"RDF Mapper"`, `"Full POST"` | `"Kraken App"` |
| `krakenpro_key` | string | Any string | — |
| `mapping_server_url` | string | WebSocket URL | `"wss://map.krakenrf.com:2096"` |
| `rdf_mapper_server` | string | HTTP URL | — |
| **VFO** | | | |
| `spectrum_calculation` | string | `"Single"`, `"All"` | `"Single"` |
| `vfo_mode` | string | `"Standard"`, `"Auto"` | `"Standard"` |
| `active_vfos` | int | 1 – 16 | `1` |
| `output_vfo` | int | -1 (all), 0 – 15 | `0` |
| `dsp_decimation` | int | ≥ 1 | `1` |
| `vfo_default_squelch_mode` | string | `"Auto"`, `"Manual"`, `"Auto Channel"` | `"Auto"` |
| `vfo_default_demod` | string | `"None"`, `"FM"` | `"None"` |
| `vfo_default_iq` | string | `"False"`, `"True"` | `"False"` |
| `max_demod_timeout` | int (s) | > 0 | `60` |
| `en_optimize_short_bursts` | bool | `true`, `false` | `false` |
| **Per-VFO** (replace `N` with 0–15) | | | |
| `vfo_freq_N` | float (Hz) | Within tuned bandwidth | center freq |
| `vfo_bw_N` | int (Hz) | ≥ 100 | `12500` |
| `vfo_fir_order_factor_N` | int | ≥ 2 | `2` |
| `vfo_squelch_N` | int (dBFS) | Any integer | `-120` |
| `vfo_squelch_mode_N` | string | `"Default"`, `"Auto"`, `"Manual"`, `"Auto Channel"` | `"Default"` |
| `vfo_demod_N` | string | `"Default"`, `"None"`, `"FM"` | `"Default"` |
| `vfo_iq_N` | string | `"Default"`, `"False"`, `"True"` | `"Default"` |

### Remote control via HTTP (legacy)

> **Note:** HTTP-based remote control via port 8081 is a legacy mechanism. The WebSocket interface above is the recommended approach and works in both GUI and headless modes without any extra server.

The `settings.json` file can still be served and uploaded via miniserve on port 8081 when `en_remote_control: true` is set and the application is running in GUI mode. This option is disabled in headless mode.

```bash
# Download current settings
curl http://KRAKEN_IP:8081/settings.json

# Upload modified settings
curl -F "path=@settings.json" http://KRAKEN_IP:8081/upload\?path\=/
```

#### Middleware API (port 8042)

The Node.js middleware also exposes a REST API for settings access:

```bash
GET  http://KRAKEN_IP:8042/settings   # retrieve current settings JSON
POST http://KRAKEN_IP:8042/settings   # send new settings JSON
```


## For Contributors

If you plan to contribute code then it must follow certain formatting style. The easiest way to apply autoformatting and check for any [PEP8](https://peps.python.org/pep-0008/) violations is to install [`pre-commit`](https://pre-commit.com/) tool, e.g., with

```bash
pip3 install --user pre-commit
```

Then from within the `krakensdr_doa` folder execute:

```bash
pre-commit install
```

that would set up git pre-commit hooks. Those will autoformat and check changed files on every consecutive commits. Once you create PR for your changes, [GitHub Actions](https://github.com/features/actions) will be executed to perform the very same checks as the hooks to make sure your code follows the formatting style and does not violate PEP8 rules.

## Upcoming Features and Known Bugs

1. [FEATURE] It would be better if the KrakenSDR controls, spectrum and/or DOA graphs could be accessible from the same page. Future work will look to integrate the controls in a sidebar.

2. [FEATURE] Wideband scanning. There should be a feature to rapidly scan through a set of frequencies over a wide bandwidth, and perform DFing on a signal in that set if it is active. To do this a rapid scan feature that does not do coherent calibration needs to be implemented first. Then when an active signal is found, calibrate as fast as possible, and do the DoA calculation on that signal for a set period of time, before returning to scan mode.

## Array Sizing Calculator and Templates

Please find the array sizing calculator at https://docs.google.com/spreadsheets/d/1w_LoJka7n38-F0a3vgaTVcSXxjXvH2Td/edit?usp=sharing&ouid=113401145893186461043&rtpof=true&sd=true. Download this file and use it in Excel.

For our own KrakenSDR branded magnetic whip antenna sets we have a paper printable array template for UCA radius spacings every 50mm linked below. Print 5 arms and one middle and cut out the template and holes so that the antenna base fits inside them. Then use a glue stick to glue the arms onto the base.

**Array Arms:** https://drive.google.com/file/d/16tjBljRIHRUfqSs5Vb5xsypVTtHK_vDl/view?usp=sharing

**Array Middle Pentagon:** https://drive.google.com/file/d/1ekBcr3fQEz1d8WlKEerOmj-JriCywHhg/view?usp=sharing

You can also 3D print a more rigid template:

**Array Arm:** https://drive.google.com/file/d/1LsiqZolMU4og2NStPewQWhIh3z6N1zb5/view?usp=sharing

**Array Middle Pentagon:** https://drive.google.com/file/d/1fn4KO7orITNJWV99XJHYu8RlZgmTl6-5/view?usp=sharing
