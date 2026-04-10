# KrakenSDR Signal Processor
#
# Copyright (C) 2018-2021  Carl Laufer, Tamás Pető
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#
# - coding: utf-8 -*-

# isort: off
from maindash import app, spectrum_fig, waterfall_fig, web_interface

# isort: on

import kraken_ws_server
from utils import fetch_dsp_data, fetch_gps_data
from views import main

app.layout = main.layout

# It is workaround for splitting callbacks in separate files (run callbacks after layout)
from callbacks import display_page, main, update_daq_params  # noqa: F401

# Start the standalone WebSocket server on its own port/thread immediately.
# This is independent of dash_devices so clients can connect and receive data
# without any browser ever opening the GUI.
kraken_ws_server.start_server(host="0.0.0.0", port=8082)

# Start the data-pump timers unconditionally at module load time.
# Previously these only started when the first browser client connected
# (callback_connect).  Starting them here ensures the signal-processor queue
# is always drained and WebSocket broadcasts always flow.
fetch_dsp_data(app, web_interface, spectrum_fig, waterfall_fig)
fetch_gps_data(app, web_interface)

if __name__ == "__main__":
    # Debug mode does not work when the data interface is set to shared-memory
    # "shmem"!
    app.run_server(debug=False, host="0.0.0.0", port=8080)