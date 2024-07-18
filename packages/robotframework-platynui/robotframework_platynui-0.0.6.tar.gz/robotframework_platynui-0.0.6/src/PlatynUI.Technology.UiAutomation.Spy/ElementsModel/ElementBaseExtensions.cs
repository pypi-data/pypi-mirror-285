using PlatynUI.Technology.UiAutomation.Client;
using PlatynUI.Technology.UiAutomation.Core;

namespace PlatynUI.Technology.UiAutomation.Spy.ElementsModel;

static class ElementBaseExtensions
{
    public static ElementBase? FindAutomationElement(this ElementBase elementBase, IUIAutomationElement element)
    {
        ElementBase? result = FindElementOnce(elementBase, element);

        if (result != null)
        {
            return result;
        }

        elementBase.Refresh();

        return FindElementOnce(elementBase, element);
    }

    private static ElementBase? FindElementOnce(ElementBase elementBase, IUIAutomationElement element)
    {
        return elementBase.Children.FirstOrDefault(e =>
        {
            if (e is UiaElement uiaElement)
            {
                return Automation.CompareElements(uiaElement.AutomationElement, element);
            }
            return false;
        });
    }
}
