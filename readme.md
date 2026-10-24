# Indian Number Reader (lakh/crore)

An NVDA add-on that reads large numbers in the Indian numbering system, lakh and crore, instead of million and billion. It works in every application: Excel, Tally, bank statements, government PDFs, web pages and more.

Author: Mukesh Jain, VisionAccess

## Download

Get the latest `.nvda-addon` file from the [Releases page](../../releases/latest). Press Enter on the downloaded file and NVDA will offer to install it.

## Examples

* 1,500,000 or 15,00,000 is read as 15 lakh
* 12,345,678 is read as 1 crore 23 lakh 45678
* Rs. 1,523,456.75 is read as Rs. 15 lakh 23456 point 7 5
* 2,500,000,000,000 is read as 2 lakh 50000 crore

Numbers below one lakh are not changed, because they are read the same way in both systems.

## Commands

* **NVDA+Alt+N**: turn automatic Indian number reading on or off.
* **NVDA+Alt+I**: read the selected text, or the current line or Excel cell, with numbers in lakh and crore. Works even when automatic reading is off.
* **NVDA+Alt+I pressed twice**: copy the text to the clipboard with Indian commas, for example 15,00,000.

You can change these keys, and assign a key to open the settings, from NVDA menu, Preferences, Input Gestures, category Indian Number Reader.

## Settings

NVDA menu, Preferences, Settings, Indian Number Reader.

* **Automatically read numbers in lakh and crore**: on by default.
* **Also convert numbers written without commas**, for example 1500000 in Excel cells: on by default.
* **Minimum and maximum digits for numbers without commas**: default 7 to 9. This keeps 6-digit PIN codes and OTPs, 10-digit mobile numbers, and long account or Aadhaar numbers from being read as lakh or crore.

Numbers with commas are always converted. Numbers joined to letters, such as INV1500000, are left as they are.

## Requirements

NVDA 2023.1 or later. Tested up to NVDA 2026.2.

## Building from source

The add-on files are in the `addon` folder. To make the `.nvda-addon` package, install Python 3 and run:

    python build.py

## License

GNU General Public License version 2. See the LICENSE file.

## Contact

VisionAccess: info@visionaccess.org
