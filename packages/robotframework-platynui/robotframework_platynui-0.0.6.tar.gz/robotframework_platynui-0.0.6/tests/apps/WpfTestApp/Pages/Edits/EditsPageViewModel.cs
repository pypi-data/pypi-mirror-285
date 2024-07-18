using System.ComponentModel.Composition;

namespace WpfTestApp.Pages.Edits;

[Export(typeof(TabPageBase))]
public class EditsPageViewModel : TabPageBase
{
    private EditsPageViewModel()
        : base("Edits") { }
}
