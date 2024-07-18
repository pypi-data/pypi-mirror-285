using Caliburn.Micro;

namespace PlatynUI.Technology.UiAutomation.Spy.ElementsModel;

public class FindResult(ElementBase element) : PropertyChangedBase, IHaveDisplayName
{
    private string _displayName = element.DisplayName;
    public string DisplayName
    {
        get => _displayName;
        set
        {
            if (value == _displayName)
            {
                return;
            }

            _displayName = value;
            NotifyOfPropertyChange();
        }
    }

    private string _fullDisplayName = element.FullDisplayName;
    public string FullDisplayName
    {
        get => _fullDisplayName;
        set
        {
            if (value == _fullDisplayName)
            {
                return;
            }

            _fullDisplayName = value;
            NotifyOfPropertyChange();
        }
    }

    private bool _isSelected;
    public bool IsSelected
    {
        get => _isSelected;
        set
        {
            if (value == _isSelected)
            {
                return;
            }

            _isSelected = value;
            NotifyOfPropertyChange();
        }
    }

    ElementBase _element = element;
    public ElementBase Element
    {
        get { return _element; }
        set
        {
            if (value == _element)
            {
                return;
            }

            _element = value;
            NotifyOfPropertyChange();
        }
    }
}
