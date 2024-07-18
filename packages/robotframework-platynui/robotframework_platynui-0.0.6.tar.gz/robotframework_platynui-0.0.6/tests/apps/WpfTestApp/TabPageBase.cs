using Caliburn.Micro;

namespace WpfTestApp;

public abstract class TabPageBase : Screen
{
    private bool _isEnabled = true;

    protected TabPageBase(string displayName)
    {
        DisplayName = displayName;
    }

    public sealed override string DisplayName
    {
        get => base.DisplayName;
        set => base.DisplayName = value;
    }

    public bool IsEnabled
    {
        get => _isEnabled;
        set
        {
            if (value == _isEnabled)
            {
                return;
            }

            _isEnabled = value;
            NotifyOfPropertyChange(() => IsEnabled);
        }
    }
}
