using System.ComponentModel.Composition;

namespace WpfTestApp.Pages.Disabled;

[Export(typeof(TabPageBase))]
public class DisabledPageViewModel : TabPageBase
{
    private DisabledPageViewModel()
        : base("Disabled")
    {
        IsEnabled = false;
    }
}
