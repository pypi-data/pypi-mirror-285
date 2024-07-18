using System.ComponentModel.Composition;
using System.Windows;

namespace WpfTestApp.Pages.SimpleControls;

[Export(typeof(TabPageBase))]
public class SimpleControlsPageViewModel : TabPageBase
{
    private SimpleControlsPageViewModel()
        : base("SimpleControls") { }

    public void DoSomething()
    {
        MessageBox.Show("Done");
    }
}
