using System;
using System.ComponentModel.Composition;
using System.Globalization;
using System.Windows.Data;
using Caliburn.Micro;

namespace WpfTestApp.Pages.ListViews;

public class SimpleItem
{
    public SimpleItem(string name, string sureName)
    {
        Name = name;
        SureName = sureName;
    }

    public string Name { get; set; }
    public string SureName { get; set; }
}

internal class SimpleItemConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
    {
        var item = value as SimpleItem;
        if (item != null && targetType == typeof(string))
        {
            return $"{item.Name} {item.SureName}";
        }

        return null;
    }

    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
    {
        return null;
    }
}

public class ComplexItem
{
    public ComplexItem(string name, string sureName, int age)
    {
        Name = name;
        SureName = sureName;
        Age = age;
    }

    public string Name { get; set; }
    public string SureName { get; set; }

    public int Age { get; set; }
}

[Export(typeof(TabPageBase))]
public class ListViewsPageViewModel : TabPageBase
{
    private ComplexItem _selectedComplexItem;
    private SimpleItem _selectedSimpleItem;

    static ListViewsPageViewModel()
    {
        var oldApplyConverterFunc = ConventionManager.ApplyValueConverter;
        var simpleItemConverter = new SimpleItemConverter();
        ConventionManager.ApplyValueConverter = (binding, bindableProperty, property) =>
        {
            if (bindableProperty.PropertyType == typeof(string) && property.PropertyType == typeof(SimpleItem))
            {
                binding.Converter = simpleItemConverter;
            }
            else
            {
                oldApplyConverterFunc(binding, bindableProperty, property);
            }
        };
    }

    private ListViewsPageViewModel()
        : base("List Views") { }

    public SimpleItem[] SimpleItems { get; } =
        {
            new SimpleItem("Tyrion", "Lennister"),
            new SimpleItem("Cersei", "Baratheon"),
            new SimpleItem("Jaime", "Lennister"),
            new SimpleItem("Daenerys", "Targaryen"),
            new SimpleItem("Jorah", "Mormont"),
            new SimpleItem("Jon", "Snow"),
            new SimpleItem("Sansa", "Stark"),
            new SimpleItem("Arya", "Stark"),
            new SimpleItem("Brandon", "Stark"),
            new SimpleItem("Theon", "Greyjoy"),
            new SimpleItem("Sandor", "Clegane"),
            new SimpleItem("Joffrey", "Baratheon"),
            new SimpleItem("Catelyn", "Stark"),
            new SimpleItem("Robb", "Stark"),
            new SimpleItem("Khal", "Drogo"),
            new SimpleItem("Eddard", "Stark"),
            new SimpleItem("Robert", "Baratheon"),
            new SimpleItem("Viserys", "Targaryen"),
            new SimpleItem("Petyr", "Baelish"),
            new SimpleItem("Samwell", "Tarly"),
            new SimpleItem("Davos", "Seaworth"),
            new SimpleItem("Stannis", "Baratheon"),
            new SimpleItem("Jeor", "Mormont"),
            new SimpleItem("Margaery", "Baratheon"),
            new SimpleItem("Tywin", "Lennister"),
            new SimpleItem("Talisa", "Stark")
        };

    public SimpleItem SelectedSimpleItem
    {
        get => _selectedSimpleItem;
        set
        {
            if (Equals(value, _selectedSimpleItem))
            {
                return;
            }

            _selectedSimpleItem = value;
            NotifyOfPropertyChange();
        }
    }

    public ComplexItem[] ComplexItems { get; } =
        {
            new ComplexItem("Tyrion", "Lennister", 40),
            new ComplexItem("Cersei", "Baratheon", 36),
            new ComplexItem("Jaime", "Lennister", 42),
            new ComplexItem("Daenerys", "Targaryen", 25),
            new ComplexItem("Jorah", "Mormont", 23),
            new ComplexItem("Jon", "Snow", 28),
            new ComplexItem("Sansa", "Stark", 21),
            new ComplexItem("Arya", "Stark", 16),
            new ComplexItem("Brandon", "Stark", 15),
            new ComplexItem("Theon", "Greyjoy", 29),
            new ComplexItem("Sandor", "Clegane", 62),
            new ComplexItem("Joffrey", "Baratheon", 18),
            new ComplexItem("Catelyn", "Stark", 52),
            new ComplexItem("Robb", "Stark", 30),
            new ComplexItem("Khal", "Drogo", 30),
            new ComplexItem("Eddard", "Stark", 53),
            new ComplexItem("Robert", "Baratheon", 34),
            new ComplexItem("Viserys", "Targaryen", 45),
            new ComplexItem("Petyr", "Baelish", 45),
            new ComplexItem("Samwell", "Tarly", 28),
            new ComplexItem("Davos", "Seaworth", 32),
            new ComplexItem("Stannis", "Baratheon", 63),
            new ComplexItem("Jeor", "Mormont", 45),
            new ComplexItem("Margaery", "Baratheon", 45),
            new ComplexItem("Tywin", "Lennister", 35),
            new ComplexItem("Talisa", "Stark", 45)
        };

    public ComplexItem SelectedComplexItem
    {
        get => _selectedComplexItem;
        set
        {
            if (Equals(value, _selectedComplexItem))
            {
                return;
            }

            _selectedComplexItem = value;
            NotifyOfPropertyChange();
        }
    }
}
