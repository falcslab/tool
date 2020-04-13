# -*- coding: UTF-8 -*-

import wx, os, sys, shutil
from datetime import datetime as dt

class FileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, fileList):
        # prefixを取得
        prefix = self.window.text_entry.GetValue()
        # 作成ディレクトリ名を設定
        dirname = 'fileRename_' + dt.now().strftime('%Y%m%d%H%M%S')

        # prefix入力確認
        if prefix == '':
            wx.MessageBox('prefixを入力してください。', '警告', wx.ICON_EXCLAMATION)
            return 0

        # リストをクリア
        self.window.listctrl.DeleteAllItems()

        # ディレクトリパスを設定
        dirpath = os.path.dirname(sys.argv[0]) + '\\' + dirname
        os.mkdir(dirpath)

        # ファイル作成日時の古い順にソート
        fileList.sort(key=os.path.getctime, reverse=False)

        # ListCtrlにアイテムを追加
        list_str = '変更前,変更後,作成日時' + '\n'
        for i, file in enumerate(fileList):
            new_filename = prefix + '_' + '{0:03d}'.format(i + 1) + os.path.splitext(file)[1]
            create_datetime = dt.fromtimestamp(os.path.getctime(file)).strftime('%Y/%m/%d %H:%M:%S')
            shutil.copyfile(file, dirpath + '/' + new_filename)

            self.window.listctrl.InsertItem(i, os.path.basename(file))
            self.window.listctrl.SetItem(i, 1, new_filename)
            self.window.listctrl.SetItem(i, 2, create_datetime)
            self.window.listctrl.SetItem(i, 3, dirpath)

            # csv出力用文字列設定
            list_str = list_str + os.path.basename(file) + ',' + new_filename + ',' + create_datetime + '\n'

        list_filepath = dirpath + '\\' + 'リネームファイルリスト.csv'
 
        # csvファイル出力
        with open(list_filepath, mode='w') as f:
            f.write(list_str)

        wx.MessageBox('ファイルリネームが完了しました。', '完了',  wx.ICON_INFORMATION)

        return 0

class App(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(1100, 600), style=wx.DEFAULT_FRAME_STYLE)

        # 二重起動防止
        self.instance = wx.SingleInstanceChecker(self.GetTitle())

        if self.instance.IsAnotherRunning():
            wx.MessageBox('%sはすでに起動中です。' % self.GetTitle(), 'エラー', wx.ICON_ERROR)
            wx.Exit()

        # パネル
        panel = wx.Panel(self, wx.ID_ANY)

        label = wx.StaticText(panel, wx.ID_ANY, 'ここにファイルをドロップ', style=wx.SIMPLE_BORDER | wx.TE_CENTER)
        label.SetBackgroundColour("#ffffe0")

        # ドロップ対象の設定
        label.SetDropTarget(FileDropTarget(self))

        # テキスト入力（ラベル）
        self.pBox = wx.BoxSizer(wx.HORIZONTAL)
        pLabel = wx.StaticText(panel, -1, 'prefix')
        self.pBox.Add(pLabel, 0, wx.RIGHT, 8)
        self.text_entry = wx.TextCtrl(panel, wx.ID_ANY)
        self.pBox.Add(self.text_entry, 1)

        # リスト
        self.listctrl = wx.ListCtrl(panel, wx.ID_ANY, style=wx.LC_REPORT)

        # カラムの設定
        self.listctrl.InsertColumn(0, '変更前', wx.LIST_FORMAT_LEFT, 200)
        self.listctrl.InsertColumn(1, '変更後', wx.LIST_FORMAT_LEFT, 200)
        self.listctrl.InsertColumn(2, '作成日時', wx.LIST_FORMAT_LEFT, 200)
        self.listctrl.InsertColumn(3, '保存先フォルダパス', wx.LIST_FORMAT_LEFT, 400)

        # レイアウト
        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(label, flag=wx.EXPAND | wx.ALL, border=10, proportion=1)
        layout.Add(self.pBox, flag=wx.EXPAND | wx.ALL, border=10)
        layout.Add(self.listctrl, flag=wx.EXPAND | wx.ALL, border=10, proportion=1)
        panel.SetSizer(layout)

        self.Show()

if __name__ == '__main__':
    app = wx.App()
    App(None, -1, 'ファイルリネームツール')
    app.MainLoop()