using System;
using System.ComponentModel.Composition;
using System.Windows;
using System.Windows.Interop;
using Microsoft.Win32;
using WpfTestApp.Interop;

namespace WpfTestApp.Pages.Buttons;

[Flags]
public enum BIF
{
    RETURNONLYFSDIRS = 0x00000001,
    DONTGOBELOWDOMAIN = 0x00000002,
    STATUSTEXT = 0x00000004,
    RETURNFSANCESTORS = 0x00000008,
    EDITBOX = 0x00000010,
    VALIDATE = 0x00000020,
    NEWDIALOGSTYLE = 0x00000040,
    BROWSEINCLUDEURLS = 0x00000080,
    USENEWUI = EDITBOX | NEWDIALOGSTYLE,
    UAHINT = 0x00000100,
    NONEWFOLDERBUTTON = 0x00000200,
    NOTRANSLATETARGETS = 0x00000400,
    BROWSEFORCOMPUTER = 0x00001000,
    BROWSEFORPRINTER = 0x00002000,
    BROWSEINCLUDEFILES = 0x00004000,
    SHAREABLE = 0x00008000,
    BROWSEFILEJUNCTIONS = 0x00010000
}

// ReSharper restore InconsistentNaming


[Export(typeof(TabPageBase))]
public class ButtonsPageViewModel : TabPageBase
{
    private bool _canDoSomething = true;
    private bool _canDoSomethingOther = true;
    private bool _isOption1;
    private bool _isOption2;
    private bool _isOption3;
    private string _selectedOption;

    private ButtonsPageViewModel()
        : base("Buttons") { }

    public bool CanDoSomething
    {
        get => _canDoSomething;
        set
        {
            if (value == _canDoSomething)
            {
                return;
            }

            _canDoSomething = value;
            NotifyOfPropertyChange();
        }
    }

    public bool CanDoSomethingOther
    {
        get => _canDoSomethingOther;
        set
        {
            if (value == _canDoSomethingOther)
            {
                return;
            }

            _canDoSomethingOther = value;
            NotifyOfPropertyChange();
        }
    }

    public bool IsOption1
    {
        get => _isOption1;
        set
        {
            if (value == _isOption1)
            {
                return;
            }

            _isOption1 = value;

            NotifyOfPropertyChange();
            if (value)
            {
                SelectedOption = "Option1";
            }
        }
    }

    public bool IsOption2
    {
        get => _isOption2;
        set
        {
            if (value == _isOption2)
            {
                return;
            }

            _isOption2 = value;

            NotifyOfPropertyChange();
            if (value)
            {
                SelectedOption = "Option2";
            }
        }
    }

    public bool IsOption3
    {
        get => _isOption3;
        set
        {
            if (value == _isOption3)
            {
                return;
            }

            _isOption3 = value;
            NotifyOfPropertyChange();

            if (value)
            {
                SelectedOption = "Option3";
            }
        }
    }

    public string SelectedOption
    {
        get => _selectedOption;
        set
        {
            if (value == _selectedOption)
            {
                return;
            }

            _selectedOption = value;
            NotifyOfPropertyChange(() => SelectedOption);
        }
    }

    public void DoSomething()
    {
        MessageBox.Show("do something");
    }

    public void DoSomethingOther()
    {
        MessageBox.Show("do something other");
    }

    public void OpenFile()
    {
        var dialog = new OpenFileDialog { Title = "Select a file" };

        if (dialog.ShowDialog() == true)
        {
            MessageBox.Show(dialog.FileName);
        }
    }

    public void OpenFolder()
    {
        dynamic dialog = Activator.CreateInstance(
            Type.GetTypeFromCLSID(new Guid("13709620-C279-11CE-A49E-444553540000"))
        );

        var b = dialog.BrowseForFolder(
            new WindowInteropHelper(Application.Current.MainWindow).Handle.ToInt32(),
            "Select a folder",
            (int)(BIF.RETURNONLYFSDIRS | BIF.USENEWUI)
        );

        if (b != null)
        {
            MessageBox.Show(b.Self.Path);
        }
    }

    public void OpenFolderNew()
    {
        var dialog = new NativeFileOpenDialog();
        dialog.SetTitle("Select a folder");

        dialog.SetOptions(FOS.FOS_PICKFOLDERS | FOS.FOS_FORCEFILESYSTEM | FOS.FOS_NOVALIDATE);

        if (dialog.Show(new WindowInteropHelper(Application.Current.MainWindow).Handle) == 0)
        {
            dialog.GetFolder(out var folder);
            folder.GetDisplayName(SIGDN.SIGDN_DESKTOPABSOLUTEPARSING, out var path);
            MessageBox.Show(path);
        }
    }
}
