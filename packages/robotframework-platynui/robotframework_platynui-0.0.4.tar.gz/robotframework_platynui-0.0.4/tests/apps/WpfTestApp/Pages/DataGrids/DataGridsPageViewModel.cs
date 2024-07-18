using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel.Composition;
using Caliburn.Micro;

namespace WpfTestApp.Pages.DataGrids;

public enum DataEnum
{
    Visible,
    NotVisible,
    Hidden
}

[Export(typeof(TabPageBase))]
public class DataGridsPageViewModel : TabPageBase
{
    private ObservableCollection<DataItem> _dataItems =
    [
        new DataItem("Bernd", "Müller", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Klaus", "Tester", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Gerda", "Tester", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Gundula", "Koslowski", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Nina", "Turtle", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Paul", "McCartney", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Ringo", "Star", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Gus", "Bakkus", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Remi", "Deal", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Jon", "Snow", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Tyrion", "Lannister", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Cersei", "Lannister", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Daenerys", "Targaryen", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Sansa", "Stark", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Arya", "Stark", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Jorah", "Mormont", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Jaime", "Lannister", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Samwell", "Tarly", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Theon", "Greyjoy", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Petyr", "Baelish", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Brienne", "of Tarth", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Sandor", "Clegane", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Alfred", "Maier", new DateTime(1970, 4, 3), DataEnum.Visible)
    ];

    private ObservableCollection<DataItem> _xceedDataItems =
    [
        new DataItem("Bernd", "Müller", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Klaus", "Tester", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Gerda", "Tester", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Gundula", "Koslowski", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Nina", "Turtle", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Paul", "McCartney", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Ringo", "Star", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Gus", "Bakkus", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Remi", "Deal", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Jon", "Snow", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Tyrion", "Lannister", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Cersei", "Lannister", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Daenerys", "Targaryen", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Sansa", "Stark", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Arya", "Stark", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Jorah", "Mormont", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Jaime", "Lannister", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Samwell", "Tarly", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Theon", "Greyjoy", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Petyr", "Baelish", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Brienne", "of Tarth", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Sandor", "Clegane", new DateTime(1970, 4, 3), DataEnum.Visible),
        new DataItem("Alfred", "Maier", new DateTime(1970, 4, 3), DataEnum.Visible)
    ];

    private DataGridsPageViewModel()
        : base("DataGrids") { }

    public ObservableCollection<DataItem> DataItems
    {
        get => _dataItems;
        set
        {
            if (Equals(value, _dataItems))
            {
                return;
            }

            _dataItems = value;
            NotifyOfPropertyChange();
            NotifyOfPropertyChange(nameof(CellOrRowHeaderSelectableDataItems));
        }
    }

    public IEnumerable<DataItem> CellOrRowHeaderSelectableDataItems => DataItems;

    public ObservableCollection<DataItem> XceedDataItems
    {
        get => _xceedDataItems;
        set
        {
            if (Equals(value, _xceedDataItems))
            {
                return;
            }

            _xceedDataItems = value;
            NotifyOfPropertyChange();
        }
    }
}

public class DataItem : PropertyChangedBase
{
    private DateTime _birthDay;
    private DataEnum _dataEnum;
    private bool _enabled;

    private string _firstName;
    private string _sureName;

    public DataItem(string firstName, string sureName, DateTime birthday, DataEnum dataEnum)
    {
        _firstName = firstName;
        _sureName = sureName;
        _birthDay = birthday;
        _dataEnum = dataEnum;
        _enabled = true;
    }

    public DataEnum DataEnum
    {
        get => _dataEnum;
        set
        {
            if (value == _dataEnum)
            {
                return;
            }

            _dataEnum = value;
            NotifyOfPropertyChange();
        }
    }

    public string FirstName
    {
        get => _firstName;
        set
        {
            if (value == _firstName)
            {
                return;
            }

            _firstName = value;
            NotifyOfPropertyChange();
        }
    }

    public string SureName
    {
        get => _sureName;
        set
        {
            if (value == _sureName)
            {
                return;
            }

            _sureName = value;
            NotifyOfPropertyChange();
        }
    }

    public bool Enabled
    {
        get => _enabled;
        set
        {
            if (value == _enabled)
            {
                return;
            }

            _enabled = value;
            NotifyOfPropertyChange();
        }
    }

    public DateTime BirthDay
    {
        get => _birthDay;
        set
        {
            if (value.Equals(_birthDay))
            {
                return;
            }

            _birthDay = value;
            NotifyOfPropertyChange();
        }
    }
}
