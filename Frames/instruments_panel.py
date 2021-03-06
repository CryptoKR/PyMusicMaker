import wx

def generate_instruments_panel(parent):
    win = wx.MDIChildFrame(parent, -1, "Instruments", size=(110, 600), pos=(136, 0),
                           style=wx.CLOSE_BOX | wx.CAPTION | wx.CLIP_CHILDREN | wx.RESIZE_BORDER)
    s = wx.BoxSizer(wx.VERTICAL)
    instrumentsPanel = Instruments(win)
    s.Add(instrumentsPanel, 1, wx.EXPAND)
    win.SetSizer(s)
    win.SetSizeHints(110, 600, 1200, 1200)
    win.Show(True)
    return instrumentsPanel


class Instruments(wx.Panel):
    def __init__(self, parent):
        self.frameParent = None
        self.associationData = {}
        self.instruments = {}
        self.parent = parent
        wx.Panel.__init__(self, parent)
        # listView initialization
        self.listView = wx.ListView(self, -1,
                                    style=wx.LC_LIST | wx.LC_SINGLE_SEL)
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(self.listView, 1, wx.EXPAND)
        self.SetSizer(s)

        self.listView.Bind(wx.EVT_LIST_BEGIN_DRAG, self.OnDragInit)
        self.listView.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnActivated)

        self.generateList(size=(20, 20))

        self.listView.Bind(wx.EVT_CONTEXT_MENU, self.showPopupMenu)

        self.listView.SetAutoLayout(True)
        self.create_menu()

    def set_frame_parent(self, frame_parent):
        self.frameParent = frame_parent

    def Destroy(self):
        try:
            super(wx.Panel, self).Destroy()
            self.parent.Destroy()
        except:
            print('already deleted')

    def get_serialization_data(self):
        return [instrumentData.get_serialization_data() for name, instrumentData in self.instruments.items()]

    def showPopupMenu(self, evt):
        position = evt.GetPosition() - self.GetScreenPosition()
        self.PopupMenu(self.menu, position)

    def add_instrument(self, instrument_class, parameters):
        if parameters.get('pluginName', '') in self.instruments or parameters.get('pluginName', '') == '':
            msg_box = wx.MessageDialog(self
                                       , 'wrong name'
                                       , 'Failed to add'
                                       , wx.OK | wx.CENTRE)
            msg_box.ShowModal()
            return False
        instrumentInstance = instrument_class(self.frameParent, **parameters)
        instrumentInstance.show_window(False)
        self.instruments[instrumentInstance.pluginName] = instrumentInstance
        self.update_instruments()
        return True

    def update_instruments(self):
        self.generateList(size=(20, 20))

    def get_selected_instrument(self):
        if self.listView.GetFirstSelected() >= 0:
            return self.instruments[self.listView.GetItemText(self.listView.GetFirstSelected())]

    def create_menu(self):
        self.menu = wx.Menu()
        # item1 = self.menu.Append(-1, 'Remove')
        self.update_instruments()

    def clear_instruments(self):
        self.listView.ClearAll()
        self.associationData.clear()

    def generateList(self, size=(50, 50)):
        self.clear_instruments()
        info = wx.ListItem()
        info.m_mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
        info.m_image = -1
        info.m_format = 0
        info.m_text = "Generators"
        self.listView.InsertColumn(0, info)
        image_list = wx.ImageList(*size)

        for key, (name, sound) in enumerate(self.instruments.items()):
            self.associationData[key] = sound
            image = image_list.Add(
                wx.Bitmap.FromRGBA(size[0], size[1], red=sound.colourRed
                                   , green=sound.colourGreen, blue=sound.colourBlue, alpha=sound.colourAlpha))
            item = self.listView.InsertItem(key
                                            , name
                                            , image)
            self.listView.SetItemData(item, key)
            self.listView.SetItemImage(item, image, wx.TreeItemIcon_Normal)

        self.listView.AssignImageList(image_list, wx.IMAGE_LIST_SMALL)
        self.Layout()

    # when item starts to be dragged
    def OnDragInit(self, event):
        try:
            item = event.GetItem()
            text = item.GetText()
            tdo = wx.TextDataObject(text)
            tds = wx.DropSource(self.listView)
            tds.SetData(tdo)
            tds.DoDragDrop(True)
        except:
            pass
    # when double clicked
    def OnActivated(self, event):
        itemb = event.GetIndex()
        item = self.associationData[itemb]
        item.show_window(True)
