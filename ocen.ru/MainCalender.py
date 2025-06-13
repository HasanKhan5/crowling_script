import wx
import wx.adv
import Global_var
class MyCalendar(wx.Frame):

    def __init__(self, *args, **kargs):
        wx.Frame.__init__(self, *args, **kargs ,size =(250,235),style= wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)
        self.panel = wx.Panel(self,size=(450, 235), pos=(0, 0), style=wx.SIMPLE_BORDER)

        self.cal = wx.adv.CalendarCtrl(self.panel, 10, wx.DateTime.Now(),pos = (0,0))
        self.cal.Bind(wx.adv.EVT_CALENDAR, self.From_Date) 

        self.Get_date1 = wx.Button(self.panel, label="From Date", pos=(60,155),size = (120,30),style=wx.NO_BORDER)
        font = wx.Font(12, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        self.Get_date1.SetFont(font)
        self.Get_date1.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.Get_date1.Bind(wx.EVT_BUTTON, self.From_Date)
        self.Get_date1.SetForegroundColour('Black')
        self.Get_date1.SetBackgroundColour('#d7d7d7')

    def From_Date(self,event):
        selected = self.cal.GetDate()
        # day = selected.Day
        From_Date = selected.Format('%d-%m-%Y')
        Global_var.fromdate = str(From_Date).strip()
        print(From_Date)
        self.Destroy() # if Second Calender was not on frame

if __name__ == '__main__':
    app = wx.App()
    frame = MyCalendar(None)
    frame.Show()
    app.MainLoop()
import collectlink