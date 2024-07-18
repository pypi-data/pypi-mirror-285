using System.Collections.ObjectModel;
using PlatynUI.Technology.UiAutomation.Core;

namespace PlatynUI.Technology.UiAutomation.Spy.ElementsModel;

public class UiaRootElement : ElementBase
{
    public UiaRootElement()
        : base(null)
    {
        IsExpanded = true;
    }

    protected override ObservableCollection<ElementBase> InitChildren()
    {
        var result = base.InitChildren();

        result.Add(new UiaElement(null, Automation.RootElement, Automation.RawViewWalker) { IsExpanded = true });

        return result;
    }

    public override void Refresh()
    {
        foreach (var child in Children)
        {
            child.Refresh();
        }
    }
}
