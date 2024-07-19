using System.ComponentModel.Composition;

namespace WpfTestApp.Pages.Trees;

[Export(typeof(TabPageBase))]
public class TreesPageViewModel : TabPageBase
{
    public TreesPageViewModel()
        : base("Trees") { }
}
