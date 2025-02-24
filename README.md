# victron-ble-bridge

A Python3 library to parse Instant Readout advertisement data from Victron devices and send them to a [web app](https://github.com/debueb/victron-ble-monitor) for visualization

Disclaimer: This software is not an officially supported interface by Victron and is provided entirely "as-is"

## Supported Devices:

* SmartShunt 500A/500mv and BMV-712/702
* Solar Chargers

## Installation

- clone this repo
- install dependencies
```bash
pip -i requirements.txt
```
- create `victron_ble/config.py` and update with your environment data
```python
CONFIG = {
    "server_url": "http://localhost:6060",

    # timeout in seconds to scan for victron bluetooth instant advertisements. Program will exit when all devices are scanned or timeout has expired. Set to 0 to scan continously.
    "timeout": 0,

    # victron devices to scan for
    # format: "Device bluetooth address": "Encryption Key"
    "devices": {
        "address1": "advertisementKey1",
        "address2": "advertisementKey2"
    }
}
```

To be able to decrypt the contents of the advertisement, you'll need to first fetch the per-device encryption key from the official Victron application. The method to do this will vary per platform.

## Fetching Device Encryption Keys
 
**OSX**

1. Install the VictronConnect app ([Android](https://play.google.com/store/apps/details?id=com.victronenergy.victronconnect), [IOS](https://apps.apple.com/us/app/victron-connect/id943840744), [Linux](https://www.victronenergy.com/support-and-downloads/software#victronconnect-app), [OSX](https://apps.apple.com/us/app/victronconnect/id1084677271?ls=1&mt=12), [Windows](https://www.victronenergy.com/support-and-downloads/software#victronconnect-app))
2. Open the app and pair with your device
3. Locate the device that you want to monitor in the list shown by the app and click on it.
4. Click on the gear icon to open the Settings for that device.
5. Open the menu and select Product Info.
6. Scroll down to Instant Readout via Bluetooth and enable the feature if it is not already enabled.
7. Click the Show button next to Instant Readout Details to display the encryption keys.
8. Copy the MAC address and advertisement key

![Screenshot of the Victron Connect product info dialog showing the instant readout settings](/docs/victron-connect-instant-readout.png)

#### Headless system
You can follow the above instruction to get the keys but you will need to pair with your headless system (using `bluetoothctl` for ex) to continue the proccess.

#### OSX

[MacOS's bleak backend](https://bleak.readthedocs.io/en/latest/backends/macos.html) uses a bluetooth UUID address instead of the more traditional MAC address to identify bluetooth devices. This UUID address is often unique to the device scanned *and* the device being scanned such that it cannot be used to connect to the same device from another computer. 

If you are going to use `victron-ble` on the same Mac computer as you have the Victron app on, follow the instructions below to retrieve the address UUID and advertisement key:

1. Install the VictronConnect app from the [Mac App Store](https://apps.apple.com/us/app/victronconnect/id1084677271?ls=1&mt=12)
2. Open the app and pair with your device
3. Enable Instand readout via Bluetooth to be able to receive advertisements from your device
4. Run the following from Terminal to dump the known keys (install `sqlite3` via Homebrew)
```bash
sqlite3 ~/Library/Containers/com.victronenergy.victronconnect.mac/Data/Library/Application\ Support/Victron\ Energy/Victron\ Connect/d25b6546b47ebb21a04ff86a2c4fbb76.sqlite 'select address,advertisementKey from advertisementKeys inner join macAddresses on advertisementKeys.macAddress == macAddresses.macAddress'
```

**Linux**

1. Download the Victron AppImage app from the Victron website.
2. Pair with your device at least once to transfer keys
3. Run the following from a terminal to dump the known keys (install `sqlite3` via your package manager)
```bash
sqlite3 ~/.local/share/Victron\ Energy/Victron\ Connect/d25b6546b47ebb21a04ff86a2c4fbb76.sqlite 'select address,advertisementKey from advertisementKeys inner join macAddresses on advertisementKeys.macAddress == macAddresses.macAddress'
```

**Windows**

1. Download the VictronConnect installer from the Victron website and install.
2. Pair with your device at least once to transfer keys
3. Open Explorer, navigate to ```%AppData%\Local\Victron Energy\Victron Connect\```
4. Open [SQLite Viewer](https://inloop.github.io/sqlite-viewer/) in a web browser of your choice
5. Drag and drop the ```d25b6546b47ebb21a04ff86a2c4fbb76.sqlite``` file from Explorer into the SQLite Viewer window

## Developing

Set `"timeout": 0` in `config.py`

```bash
python victron_ble/cli.py scan
```

Start up the [web app](https://github.com/debueb/victron-ble-monitor)

## Automating

Set `"timeout": 10` in `config.py`

Add the following line in your `crontab` to update your server every  minute

```bash
*/1 * * * * python3 /path/to/project/victron_ble/cli.py scan`
```