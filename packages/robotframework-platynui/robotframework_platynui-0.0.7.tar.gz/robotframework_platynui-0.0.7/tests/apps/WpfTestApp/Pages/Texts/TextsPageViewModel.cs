using System.ComponentModel.Composition;

namespace WpfTestApp.Pages.Texts;

[Export(typeof(TabPageBase))]
public class TextsPageViewModel : TabPageBase
{
    private TextsPageViewModel()
        : base("Texts") { }
}
