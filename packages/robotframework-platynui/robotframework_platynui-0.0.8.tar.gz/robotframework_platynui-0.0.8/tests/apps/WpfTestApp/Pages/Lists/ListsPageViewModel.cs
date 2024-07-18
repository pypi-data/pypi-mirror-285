using System;
using System.Collections.ObjectModel;
using System.ComponentModel.Composition;

namespace WpfTestApp.Pages.Lists;

[Export(typeof(TabPageBase))]
public class ListsPageViewModel : TabPageBase
{
    private ObservableCollection<string> _multiSelectableListBoxItems =
    [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December"
    ];

    private ObservableCollection<string> _readonlyComboBoxItems =
    [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December"
    ];

    private string _selectedMultiSelectableListBoxItem;

    private string _selectedReadonlySimpleComboBoxItem;
    private string _selectedSimpleComboBoxItem;
    private string _selectedSimpleEditableComboBoxItem;

    private string _selectedSimpleListBoxItem;

    private string _selectedSimpleVirtualizedListBoxItem;
    private string _selectedVirtualizedMultiSelectableListBoxItem;

    private ObservableCollection<string> _simpleComboBoxItems =
    [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December"
    ];

    private ObservableCollection<string> _simpleEditableComboBoxItems =
    [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December"
    ];

    private ObservableCollection<string> _simpleListBoxItems =
    [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December"
    ];

    private ObservableCollection<string> _simpleVirtualizedListBoxItems =
    [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December"
    ];

    private ObservableCollection<string> _virtualizedMultiSelectableListBoxItems =
    [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December"
    ];

    private ListsPageViewModel()
        : base("Lists")
    {
        //var random = new Random();
        //for (var i = 0; i < 100; i++)
        //{
        //    _simpleVirtualizedListBoxItems.Insert(random.Next(_simpleVirtualizedListBoxItems.Count - 2) + 1, CreateRandomString());
        //}
    }

    public ObservableCollection<string> SimpleListBoxItems
    {
        get => _simpleListBoxItems;
        set
        {
            if (Equals(value, _simpleListBoxItems))
            {
                return;
            }

            _simpleListBoxItems = value;
            NotifyOfPropertyChange();
        }
    }

    public string SelectedSimpleListBoxItem
    {
        get => _selectedSimpleListBoxItem;
        set
        {
            if (value == _selectedSimpleListBoxItem)
            {
                return;
            }

            _selectedSimpleListBoxItem = value;
            NotifyOfPropertyChange();
        }
    }

    public ObservableCollection<string> SimpleVirtualizedListBoxItems
    {
        get => _simpleVirtualizedListBoxItems;
        set
        {
            if (Equals(value, _simpleListBoxItems))
            {
                return;
            }

            _simpleVirtualizedListBoxItems = value;
            NotifyOfPropertyChange();
        }
    }

    public string SelectedSimpleVirtualizedListBoxItem
    {
        get => _selectedSimpleVirtualizedListBoxItem;
        set
        {
            if (value == _selectedSimpleVirtualizedListBoxItem)
            {
                return;
            }

            _selectedSimpleVirtualizedListBoxItem = value;
            NotifyOfPropertyChange();
        }
    }

    public ObservableCollection<string> MultiSelectableListBoxItems
    {
        get => _multiSelectableListBoxItems;
        set
        {
            if (Equals(value, _multiSelectableListBoxItems))
            {
                return;
            }

            _multiSelectableListBoxItems = value;
            NotifyOfPropertyChange();
        }
    }

    public string SelectedMultiSelectableListBoxItem
    {
        get => _selectedMultiSelectableListBoxItem;
        set
        {
            if (value == _selectedMultiSelectableListBoxItem)
            {
                return;
            }

            _selectedMultiSelectableListBoxItem = value;
            NotifyOfPropertyChange();
        }
    }

    public ObservableCollection<string> VirtualizedMultiSelectableListBoxItems
    {
        get => _virtualizedMultiSelectableListBoxItems;
        set
        {
            if (Equals(value, _virtualizedMultiSelectableListBoxItems))
            {
                return;
            }

            _virtualizedMultiSelectableListBoxItems = value;
            NotifyOfPropertyChange();
        }
    }

    public string SelectedVirtualizedMultiSelectableListBoxItem
    {
        get => _selectedVirtualizedMultiSelectableListBoxItem;
        set
        {
            if (value == _selectedVirtualizedMultiSelectableListBoxItem)
            {
                return;
            }

            _selectedVirtualizedMultiSelectableListBoxItem = value;
            NotifyOfPropertyChange();
        }
    }

    public ObservableCollection<string> SimpleComboBoxItems
    {
        get => _simpleComboBoxItems;
        set
        {
            if (Equals(value, _simpleComboBoxItems))
            {
                return;
            }

            _simpleComboBoxItems = value;
            NotifyOfPropertyChange();
        }
    }

    public string SelectedSimpleComboBoxItem
    {
        get => _selectedSimpleComboBoxItem;
        set
        {
            if (value == _selectedSimpleComboBoxItem)
            {
                return;
            }

            _selectedSimpleComboBoxItem = value;
            NotifyOfPropertyChange();
        }
    }

    public ObservableCollection<string> SimpleEditableComboBoxItems
    {
        get => _simpleComboBoxItems;
        set
        {
            if (Equals(value, _simpleEditableComboBoxItems))
            {
                return;
            }

            _simpleEditableComboBoxItems = value;
            NotifyOfPropertyChange();
        }
    }

    public string SelectedSimpleEditableComboBoxItem
    {
        get => _selectedSimpleEditableComboBoxItem;
        set
        {
            if (value == _selectedSimpleEditableComboBoxItem)
            {
                return;
            }

            _selectedSimpleEditableComboBoxItem = value;
            NotifyOfPropertyChange();
        }
    }

    public ObservableCollection<string> ReadonlyComboBoxItems
    {
        get => _readonlyComboBoxItems;
        set
        {
            if (Equals(value, _readonlyComboBoxItems))
            {
                return;
            }

            _readonlyComboBoxItems = value;
            NotifyOfPropertyChange();
        }
    }

    public string SelectedReadonlyComboBoxItem
    {
        get => _selectedReadonlySimpleComboBoxItem;
        set
        {
            if (value == _selectedReadonlySimpleComboBoxItem)
            {
                return;
            }

            _selectedReadonlySimpleComboBoxItem = value;
            NotifyOfPropertyChange();
        }
    }

    private string CreateRandomString()
    {
        //const string chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 !#*+-/";
        //var random = new Random(87);
        //return new string(
        //    Enumerable.Repeat(chars, 8)
        //              .Select(s => s[random.Next(s.Length)])
        //              .ToArray());

        return Guid.NewGuid().ToString();
    }
}
