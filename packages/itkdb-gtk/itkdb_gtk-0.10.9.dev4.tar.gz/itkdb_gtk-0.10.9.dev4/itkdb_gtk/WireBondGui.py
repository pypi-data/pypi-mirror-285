#!/usr/bin/env python3
"""Wirebonding GUI for PSB."""

import sys
import json
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, Gdk

try:
    import itkdb_gtk

except ImportError:
    from pathlib import Path
    cwd = Path(__file__).parent.parent
    sys.path.append(cwd.as_posix())
    import itkdb_gtk

__HELP_LINK__="https://itkdb-gtk.docs.cern.ch/wirebondTest.html"

from itkdb_gtk import dbGtkUtils
from itkdb_gtk import ITkDBlogin, ITkDButils, UploadTest

test_parameters = {
        "Repaired Row 1": "REPAIRED_FRONTEND_ROW1",
        "Failed Row 1": "FAILED_FRONTEND_ROW1",
        "Repaired Row 2": "REPAIRED_FRONTEND_ROW2",
        "Failed Row 2": "FAILED_FRONTEND_ROW2",
        "Repaired Row 3": "REPAIRED_FRONTEND_ROW3",
        "Failed Row 3": "FAILED_FRONTEND_ROW3",
        "Repaired Row 4": "REPAIRED_FRONTEND_ROW4",
        "Failed Row 4": "FAILED_FRONTEND_ROW4",
        "Repaired Hyb->PB": "REPAIRED_HYBRID_TO_PB",
        "Failed HyB->PB": "FAILED_HYBRID_TO_PB",
        "Repaired Module->Frame": "REPAIRED_MODULE_TO_FRAME",
        "Failed Module->Frame": "FAILED_MODULE_TO_FRAME"
}

# module_param[iring][i_sensor][i_hybrid][i_row]
module_param = {
    0: [
        [
            [[255, 830], [1343, 1918], [2431, 3006], [3519, 4094]],
            [[831, 1342], [1919, 2430], [3007, 3518], [4095, 4606]],
        ]
    ],
    1: [
        [
            [[271, 974], [1615, 2318], [2959, 3662], [4303, 5006]],
            [[975, 1614], [2319, 2958], [3663, 4302], [5007, 5646]],
        ]
    ],
    2: [
        [
            [[201, 968], [969, 1736], [1737, 2504], [2505, 3272]]
        ]
    ],
    3: [
        [
            [[566, 1013], [2358, 2805], [4150, 4597], [5942, 6389]],
            [[1462, 1909], [3254, 3701], [5046, 5493], [6838, 7285]]
        ],
        [
            [[1014, 1461], [2806, 3253], [4598, 5045], [6390, 6837]],
            [[1910, 2357], [3702, 4149], [5494, 5941], [7286, 7733]]
        ]
    ],
    4: [
        [
            [[318, 829], [1342, 1853], [2366, 2877], [3390, 3901]]
        ],
        [
            [[830, 1341], [1854, 2365], [2878, 3389], [3902, 4413]]
        ]
    ],
    5: [
        [
            [[332, 907], [1484, 2059], [2636, 3211], [3788, 4363]]
        ],
        [
            [[908, 1483], [2060, 2635], [3212, 3787], [4364, 4939]]
        ]
    ],
}

def wire2strip(mod_par, irow, iwire):
    """Convert from wirebond index to strip_number."""
    for sensor in mod_par:
        for hyb in sensor:
            rng = hyb[irow]
            if iwire>= rng[0] and iwire<=rng[1]:
                if irow % 2:
                    ichan = 2*(iwire-rng[0]) + 1
                else:
                    ichan = 2*(iwire-rng[0])

                return ichan

    return None


def find_holes(chan_list, min_chan=0, max_chan=999999):
    """Find groups of consecutive channels."""
    out = sorted(chan_list)
    nchan = 0
    last_chan = -1
    ichan = -1
    holes = []
    for chan in out:
        if chan < min_chan or chan > max_chan:
            continue

        if last_chan < 0:
            last_chan = chan
            continue

        if chan - last_chan > 1:
            if nchan:
                holes.append([ichan, nchan])
            nchan = 0
            ichan = -1
        else:
            if last_chan < max_chan and chan >= max_chan:
                # WE are in another sensor
                holes.append([ichan, nchan])
                nchan = 0
                ichan = -1
                last_chan = chan
                continue

            nchan += 1
            if ichan < 0:
                ichan = last_chan
                nchan += 1

        last_chan = chan

    if nchan:
        holes.append([ichan, nchan])

    return holes


class HybridHoles:
    """Holes in hybrid bomds.

    Holes are defined by a list [first_chan, n_chan].
    """

    def __init__(self, param, hid=0):
        """Initialization.

        Args:
            param: Hybrid wirebon parameters.

        """
        self.id = hid
        self.param = param
        self.nchan = 0
        for min_chan, max_chan in param:
            self.nchan += (max_chan-min_chan+1)

        self.holes = [[] for irow in range(4)]
        self.channels = [[] for irow in range(4)]

    def add_channel(self, irow, ichan)->bool:
        """Add a new channel in row.

        Args:
            irow: rown number
            ichan: channel number

        Returns:
            True if added, False otherwise.

        """
        first_chan = self.param[irow][0]
        last_chan = self.param[irow][1]
        if isinstance(ichan, list) or isinstance(ichan, tuple):
            nadded = 0
            for ich in ichan:
                if ich >= first_chan and ich <= last_chan:
                    self.channels[irow].append(ich)
                    nadded += 1

            self.channels[irow] = sorted(self.channels[irow])
            return nadded>0
        else:
            if ichan >= first_chan and ichan <= last_chan:
                self.channels[irow].append(ichan)
                return True
            else:
                return False

    def get_n_unconnected(self):
        """Count number of unconnected channels.

        Return a list, one item per row.
        """
        nchan = []
        for row in self.holes:
            nch = 0
            for h in row:
                nch += h[1]

            nchan.append(nch)

        return nchan

    def get_max_consecutive(self):
        """Returns the largest 'hole'."""
        mx_width = []

        for row in self.holes:
            mxW = -1
            for h in row:
                if h[1] > mxW:
                    mxW = h[1]

            mx_width.append(mxW)

        return mx_width

    def get_sensor_holes(self):
        """Compute holes in 'sensor' strips.

        Each hybrid has 2 sensor segments corresponding to
        rows (1,2) and (3, 4).

        Return a list of [sensor, hybrid, segment, ichan, width]
        """
        holes = []
        channels = [[], []]
        for irow, row in enumerate(self.channels):
            isegment = int(irow/2)
            for ich in row:
                rng = self.param[irow]
                if irow % 2:
                    chan = 2*(ich-rng[0]) + 1
                else:
                    chan = 2*(ich-rng[0])

                channels[isegment].append(chan)

            channels[isegment] = sorted(channels[isegment])

        for isegment, S in enumerate(channels):
            H = find_holes(S)
            if len(H)>0:
                out = [ [0, self.id, isegment, chan, width] for chan, width in H ]
                holes.extend(out)

        return holes


class SensorHoles:
    """Holes in sensor."""

    def __init__(self, param, sid=0):
        """Initialization.

        Args:
            param: sensor wirebon params
        """
        self.id = sid
        self.param = param
        self.nchan = 0
        self.nhybrid = len(param)
        self.hybrids = []
        for i, P in enumerate(param):
            H = HybridHoles(P, hid=i)
            self.hybrids.append(H)
            self.nchan += H.nchan

    def get_n_hyb(self):
        """Return number of hybrids."""
        return len(self.hybrids)

    def get_hybrid(self, i):
        """Return i-th hybrid."""
        return self.hybrids[i]

    def get_max_consecutive(self):
        """Max number of consecutive unconnected channels.

        This is ordered by row.
        """
        mx_width = [0, 0, 0, 0]
        for hyb in self.hybrids:
            mxW = hyb.get_max_consecutive()
            for j in range(4):
                if mxW[j] > mx_width[j]:
                    mx_width[j] = mxW[j]

        return mx_width

    def get_n_unconnected(self):
        """Count number of unconnected channels.

        Return a list, one item per row.
        """
        nchan = [0, 0, 0, 0]
        for hyb in self.hybrids:
            nc = hyb.get_n_unconnected()
            for i, n in enumerate(nc):
                nchan[i] += n

        return nchan

    def get_sensor_holes(self):
        """Return holes sensor.

        Return a list of [sensor, hybrid, segment, ichan, width]
        """
        holes = []
        for hyb in self.hybrids:
            H = hyb.get_sensor_holes()
            for _, ih, isegment, ichan, width in H:
                holes.append([self.id, ih, isegment, ichan, width])

        return holes


class ModuleHoles:
    """Holes in Modules."""

    def __init__(self, param):
        """Initialization.

        Args:
            param: module wirebond params
        """
        self.nsensor = len(param)
        self.nchan = 0
        self.sensors = []
        for i, P in enumerate(param):
            S = SensorHoles(P, sid=i)
            self.sensors.append(S)
            self.nchan += S.nchan

    def get_max_consecutive(self):
        """Max number of consecutive unconnected channels.

        This is ordered by row.
        """
        mx_width = [-1, -1, -1, -1]
        for S in self.sensors:
            mxW = S.get_max_consecutive()
            for j in range(4):
                if mxW[j] > mx_width[j]:
                    mx_width[j] = mxW[j]

        return mx_width

    def get_sensor_holes(self) -> list:
        """Return. holesin sensor strips.

        Return a list of [sensor, hybrid, segment, ichan, width]
        """
        holes = []
        for S in self.sensors:
            for _, ihyb, isegment, ichan, width in S.get_sensor_holes():
                holes.append([S.id, ihyb, isegment, ichan, width])

        return holes

    def get_n_unconnected(self) -> list:
        """Count number of unconnected channels.

        Return a list, one item per row.
        """
        nchan = [0, 0, 0, 0]
        for S in self.sensors:
            nc = S.get_n_unconnected()
            for i, n in enumerate(nc):
                nchan[i] += n

        return nchan

    def get_total_unconnected(self) -> int:
        """Return total number of unconnected wires."""
        unc = self.get_n_unconnected()
        out = 0
        for v in unc:
            out += v

        return int(out)


def get_module_param(SN):
    """Get parameters of module type.

    Args:
        SN: Serial Number

    Returns:
        list: list with bond numbers.
    """
    if len(SN) != 14 or SN[:3]!="20U":
        raise ValueError("Wrong serial number {}".format(SN))

    if SN[3:5] != "SE":
        raise ValueError("Cannot handle barrel modules yet.")

    mod_type  = SN[5:7]
    if mod_type[0] != "M":
        raise ValueError("Does not seem to be a RingModule: {}".format(SN))

    ring = int(mod_type[-1])
    param = module_param[ring]

    return param


class WireBond(dbGtkUtils.ITkDBWindow):
    """Main window."""

    def __init__(self, session, title="", help_link=__HELP_LINK__):
        """Initialization."""
        super().__init__(title=title, session=session, help_link=help_link)
        self.pdb = None
        self.models = {}
        self.holes = {}
        self.institute = "IFIC"
        self.inst_combo = None
        self.module_SN = None
        self.alternativeID = None
        self.combo = None
        self.tree = None
        self.init_window()

    def init_window(self):
        """Creates the GUI."""
        self.hb.props.title = "Wire Bond"

        # Button to upload
        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="document-send-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.set_tooltip_text("Click to upload test")
        button.connect("clicked", self.upload_test)
        self.hb.pack_end(button)

        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="document-save-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.set_tooltip_text("Click to save test file")
        button.connect("clicked", self.save_test)
        self.hb.pack_end(button)

        # Button to upload
        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="document-open-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.set_tooltip_text("Click to read local data file.")
        button.connect("clicked", self.read_file)
        self.hb.pack_end(button)

        # Data panel
        grid = Gtk.Grid(column_spacing=5, row_spacing=1)

        # The shipment receiver
        institute = self.create_institute_combo()
        institute.connect("changed", self.on_institute)
        institute.set_tooltip_text("Select the Institute.")
        dbGtkUtils.set_combo_iter(institute, self.institute)
        grid.attach(Gtk.Label(label="Institute"), 0, 0, 1, 1)
        grid.attach(institute, 1, 0, 1, 1)
        self.inst_combo = institute


        for i, tit in enumerate(["Operator", "Bond Machine", "Wire Batch", "SN", "Date"]):
            lbl = Gtk.Label(label=tit)
            lbl.set_xalign(0)
            grid.attach(lbl, 0, i+1, 1, 1)

        self.operator = dbGtkUtils.new_small_text_entry()
        self.machine = dbGtkUtils.new_small_text_entry()
        self.batch = dbGtkUtils.new_small_text_entry()
        #self.SN = dbGtkUtils.new_small_text_entry()

        self.SN = itkdb_gtk.dbGtkUtils.TextEntry(small=True)
        self.SN.connect("text-changed", self.on_SN_changed)


        self.date = dbGtkUtils.TextEntry(small=True)
        self.date.entry.set_text(ITkDButils.get_db_date())
        self.date.connect("text_changed", self.new_date)

        grid.attach(self.operator,      1, 1, 1, 1)
        grid.attach(self.machine,       1, 2, 1, 1)
        grid.attach(self.batch,         1, 3, 1, 1)
        grid.attach(self.SN.entry,      1, 4, 1, 1)
        grid.attach(self.date.widget,   1, 5, 1, 1)

        self.mainBox.pack_start(grid, True, True, 0)

        # Prepare combo and all the models
        lbl = Gtk.Label(label="Choose section.")
        lbl.set_xalign(0)
        self.mainBox.pack_start(lbl, True, True, 0)

        combo = self.create_combo()
        self.mainBox.pack_start(combo, True, True, 0)

        # The tree view
        scrolled = self.create_tree_view()
        self.mainBox.pack_start(scrolled, True, True, 5)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.mainBox.pack_start(box, False, False, 0)
        dbGtkUtils.add_button_to_container(box, "Add Bond",
                                           "Click to add a new bond.",
                                           self.add_item)

        dbGtkUtils.add_button_to_container(box, "Remove Bond",
                                           "Click to remove selected bond.",
                                           self.remove_item)

        #
        # The text view and buffer
        #
        self.mainBox.pack_start(self.message_panel.frame, True, True, 0)
        self.write_message("wirebond GUI\n")

    def on_institute(self, combo):
        """Institute changed."""
        name = self.get_institute_from_combo(combo)
        if name:
            self.institute = name

    def on_SN_changed(self, entry, value):
        """New SN given. Ask in PDB,"""
        if len(value) <= 0:
            return None


        obj = itkdb_gtk.ITkDButils.get_DB_component(self.session, value)
        if obj is not None:
            entry.set_text(obj["serialNumber"])
            self.alternativeID = obj["alternativeIdentifier"]

        else:
            itkdb_gtk.dbGtkUtils.complain("Invalid SN", value)

    def on_name_combo_changed(self, combo):
        """Change model in TreeView."""
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            param = model[tree_iter][1]
            view_model = self.models[param]
            self.tree.set_model(view_model)
        else:
            self.write_message("Cannot find model for {}".format(param))

    def create_combo(self):
        """Create the combo."""
        model = Gtk.ListStore(str, str)
        for txt, param in test_parameters.items():
            model.append([txt, param])

            M = Gtk.ListStore(str, str)
            M.append(["", ""])
            self.models[param] = M

        self.combo = Gtk.ComboBox.new_with_model_and_entry(model)
        self.combo.set_entry_text_column(0)
        self.combo.set_active(0)
        self.combo.connect("changed", self.on_name_combo_changed)
        return self.combo

    def create_tree_view(self, size=150):
        """Creates the tree vew with the attachmens."""
        tree_iter = self.combo.get_active_iter()
        combo_model = self.combo.get_model()
        param = combo_model[tree_iter][1]
        model = self.models[param]

        self.tree = Gtk.TreeView(model=model)
        self.tree.connect("button-press-event", self.button_pressed)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(self.tree)
        scrolled.set_size_request(-1, size)

        renderer = Gtk.CellRendererText()
        renderer.set_property("editable", True)
        renderer.connect("edited", self.channel_edited)
        column = Gtk.TreeViewColumn("Channel", renderer, text=0)
        self.tree.append_column(column)

        renderer = Gtk.CellRendererText()
        renderer.set_property("editable", True)
        renderer.connect("edited", self.failure_edited)
        column = Gtk.TreeViewColumn("Failure", renderer, text=1)
        self.tree.append_column(column)

        return scrolled

    def text_edited(self, icol, path, text):
        """Text has been edited in the TreeView"""
        if len(text) == 0:
            return

        model = self.tree.get_model()

        n_child = model.iter_n_children()
        current_child = int(path)
        if n_child-current_child == 1:
            model.append(["", ""])

        model[path][icol] = text

    def channel_edited(self, widget, path, text):
        """Handles edition in channel number cell."""
        if not text.isnumeric():
            dbGtkUtils.complain("Wrong channel number", "Invalid channel number: {}".format(text))
            return

        self.text_edited(0, path, text)

    def failure_edited(self, widget, path, text):
        """Handles edition in comment."""
        self.text_edited(1, path, text)


    def new_date(self, entry, value):
        """new date given at input."""
        d = dbGtkUtils.parse_date_as_string(value)
        if d is not None:
            self.date.set_text(d)

    def button_pressed(self, tree, event):
        """Button pressed."""
         # double click shows attachments
        if event.button == 1 and event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            #self.write_message("This is a double click.\n")
            return

        if event.button != 3:
            return

        # Create popup menu
        select = self.tree.get_selection()
        model, lv_iter = select.get_selected()
        values = None
        if lv_iter:
            values = model[lv_iter]

        else:
            P = tree.get_path_at_pos(event.x, event.y)
            if P:
                lv_iter = model.get_iter(P[0])
                values = model[lv_iter]

        if not values:
            return

        menu = Gtk.Menu()

        item_show = Gtk.MenuItem(label="Delete")
        item_show.connect("activate", self.on_delete_item, (model, lv_iter, values))
        menu.append(item_show)

        menu.show_all()
        menu.popup_at_pointer(event)

    def on_delete_item(self, item, data):
        """Delete bond in list view."""
        model, lv_iter, _ = data
        model.remove(lv_iter)

    def remove_item(self, *args):
        """REmoves selected bond."""
        select = self.tree.get_selection()
        model, lv_iter = select.get_selected()
        if lv_iter:
            model.remove(lv_iter)

    def add_item(self, *args):
        """Adds a new item in the current model."""
        out = dbGtkUtils.get_a_list_of_values("Add Item", ["Channel", "Comment"])
        if len(out) == 2:
            model = self.tree.get_model()
            model[-1] = out
            model.append(["", ""])

    def quit(self, *args):
        """Quits the application."""
        if self.pdb:
            self.pdb.die()

        self.hide()
        self.destroy()

    def compute_unconnected(self):
        """Compute number of unconnected."""
        try:
            param = get_module_param(self.SN.get_text())
        except ValueError as E:
            dbGtkUtils.complain("Wrong SN number", str(E))

        M = ModuleHoles(param=param)

        for test in test_parameters.values():
            if test.find("FAILED") < 0:
                continue
            if test.find("ROW") < 0:
                continue

            irow = int(test[-1]) - 1

            # Get list of all channels with wirebond notation.
            model = self.models[test]
            it = model.get_iter_first()
            out = []
            while it:
                chan, _ = model[it]
                if len(chan) > 0:
                    out.append(int(chan))

                it = model.iter_next(it)

            # Translate to sensor, hybrids, etc.
            for S in M.sensors:
                for H in S.hybrids:
                    H.add_channel(irow, out)
                    H.holes[irow] = find_holes(H.channels[irow])


        # Now get sensor strips.
        unconnected = M.get_n_unconnected()
        mx_consecutive = M.get_max_consecutive()
        module_holes = M.get_sensor_holes()

        out = {}
        for irow in range(4):
            key = "MAX_CONT_UNCON_ROW{}".format(irow+1)
            out[key] = mx_consecutive[irow]

        mxW = 0
        self.write_message("Found {} clusters of unconnected strips in sensor.\n".format(len(module_holes)))
        for H in module_holes:
            self.write_message("{}\n".format(str(H)))
            if H[-1] > mxW:
                mxW = H[-1]

        if mxW > 0:
            self.write_message("Max width: {}". format(mxW))

        out["MAX_UNCON_SENSOR_CHAN"] = mxW
        nstrips = 0
        for v in unconnected:
            nstrips += v

        out["TOTAL_PERC_UNCON_SENSOR_CHAN"] = nstrips/M.nchan

        return out

    def get_unconnected(self, skeleton):
        """Fill the test DTO with unconnected information."""
        out = self.compute_unconnected()
        for key, val in out.items():
            skeleton["results"][key] = val

    def read_file(self, *args):
        """Read local data file."""
        dialog = Gtk.FileChooserDialog(
            title="Please choose a file",
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )
        filter_text = Gtk.FileFilter()
        filter_text.set_name("JSON files")
        filter_text.add_mime_type("application/json")
        dialog.add_filter(filter_text)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            ofile = dialog.get_filename()
            self.write_message("Loading data from {}\n".format(ofile))
            with open(ofile, 'r', encoding="utf-8") as data_file:
                data = json.load(data_file)
                self.parse(data)

        dialog.hide()
        dialog.destroy()

    def parse(self, data):
        """Parses a JSon dictionary."""
        try:
            dbGtkUtils.set_combo_iter(self.inst_combo, data["institution"])
        except KeyError:
            self.write_message("institution value is not in the loaded file.")

        self.operator.set_text(data["properties"]["OPERATOR"])
        self.machine.set_text(data["properties"]["BOND_MACHINE"])
        self.batch.set_text(data["properties"]["BONDWIRE_BATCH"])
        self.SN.set_text(data["component"])
        self.date.set_text(data["date"])
        for key, val in data["results"].items():
            model = self.models[key]
            model.clear()
            for chan, msg in val.items():
                model.append([chan, msg])

            model.append(["", ""])

    def get_list_of_channels(self, data):
        """Creates the lists of channels."""
        for key, model in self.models.items():
            lv_iter = model.get_iter_first()
            out = {}
            while lv_iter:
                chan, comm = model[lv_iter]
                if len(chan) > 0:
                    out[chan] = comm

                lv_iter = model.iter_next(lv_iter)

            data["results"][key] = out

    def save_test(self, *args):
        """Save Test file."""
        dialog = Gtk.FileChooserDialog(
            title="Please choose a file", parent=self, action=Gtk.FileChooserAction.SAVE
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )
        filter_text = Gtk.FileFilter()
        filter_text.set_name("JSON files")
        filter_text.add_mime_type("application/json")
        dialog.add_filter(filter_text)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            ofile = dialog.get_filename()
            data = self.get_test_data()
            with open(ofile, 'w', encoding="UTF-8") as of:
                json.dump(data, of, indent=3)

        dialog.hide()
        dialog.destroy()

    def get_test_data(self):
        """Get the test data."""
        data = {
            "institution": self.institute,
            "date": ITkDButils.get_db_date(),
            "properties": {},
            "results": {},
            "comments": [],
            "defects": []
        }
        self.get_test_header(data)
        self.get_list_of_channels(data)
        return data

    def get_test_header(self, data):
        """Get Basic test data."""
        SN = self.SN.get_text()
        operator = self.operator.get_text()
        machine = self.machine.get_text()
        batch = self.batch.get_text()

        if not SN or len(SN)==0:
            SN = dbGtkUtils.get_a_value("Module Serial Number",
                                        "Module serial Number is missing")

        if len(operator) == 0 or len(machine) == 0:
            values = dbGtkUtils.get_a_list_of_values(
                "Missing Values",
                ["SN", "Operator", "Wire Bonder"],
                defaults=[SN, operator, machine],
            )
            if len(values) == 4:
                SN, operator, machine = values
            else:
                self.write_message("Something went wrong while requesting missing information.")

        data["component"] = SN
        data["properties"]["OPERATOR"] = operator
        data["properties"]["BOND_MACHINE"] = machine
        data["properties"]["BONDWIRE_BATCH"] = batch
        data["institution"] = self.institute
        if data["runNumber"] == "-1":
            data["runNumber"] = "1"

        data["date"] = self.date.get_text()



    def upload_test(self, *args):
        """Upload test."""
        if self.session is None:
            self.pdb = ITkDBlogin.ITkDBlogin()
            client = self.pdb.get_client()
            if client is None:
                dbGtkUtils.complain("Could not connect to DB with provided credentials.")
                self.pdb.die()

            else:
                self.session = client

        defaults = {
            "institution": self.institute,
            "runNumber": "1",
            "date":  ITkDButils.get_db_date()
        }
        skeleton = ITkDButils.get_test_skeleton(self.session, "MODULE", "MODULE_WIRE_BONDING", defaults)

        self.get_test_header(skeleton)
        self.get_list_of_channels(skeleton)
        self.get_unconnected(skeleton)

        uploadW = UploadTest.UploadTest(self.session, payload=skeleton)
        # uploadW.run()


def main():
    """Main entry."""
    dlg = ITkDBlogin.ITkDBlogin()
    client = dlg.get_client()
    if client is None:
        print("Could not connect to DB with provided credentials.")
        dlg.die()
        sys.exit()

    client.user_gui = dlg


    win = WireBond(client, title="WireBond")
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    try:
        Gtk.main()

    except KeyboardInterrupt:
        print("Arrrgggg!!!")

    dlg.die()

if __name__ == "__main__":
    main()
