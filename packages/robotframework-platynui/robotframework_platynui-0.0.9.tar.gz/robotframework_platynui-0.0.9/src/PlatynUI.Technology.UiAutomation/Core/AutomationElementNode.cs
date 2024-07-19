using PlatynUI.Technology.UiAutomation.Client;

namespace PlatynUI.Technology.UiAutomation.Core;

public class AutomationElementAttribute(int id, string name, Func<AutomationElementAttribute, object?> value_getter)
    : IAttribute
{
    private readonly Func<AutomationElementAttribute, object?> _value_getter = value_getter;

    public int Id { get; } = id;
    public string Name { get; } = name;

    public object? Value
    {
        get => _value_getter(this);
    }

    public string NamespaceURI => "http://platynui.io/raw";
}

public class AutomationElementNode(
    Node<IUIAutomationElement, AutomationElementAttribute>? parent,
    IUIAutomationElement element,
    bool findVirtual = false
) : Node<IUIAutomationElement, AutomationElementAttribute>(parent, element, findVirtual)
{
    public AutomationElementNode(IUIAutomationElement element, bool findVirtual = false)
        : this(null, element, findVirtual) { }

    public override string NamespaceURI => "http://platynui.io/raw";

    List<Node<IUIAutomationElement, AutomationElementAttribute>>? _children;

    public override List<Node<IUIAutomationElement, AutomationElementAttribute>> Children
    {
        get { return _children ??= GetChildren(); }
    }

    public override string LocalName => Element.GetCurrentControlTypeName();

    private List<Node<IUIAutomationElement, AutomationElementAttribute>> GetChildren()
    {
        return Element
            .EnumerateChildren(Automation.RawViewWalker, FindVirtual)
            .Select(x => new AutomationElementNode(this, x, FindVirtual))
            .Cast<Node<IUIAutomationElement, AutomationElementAttribute>>()
            .ToList();
    }

    public override Node<IUIAutomationElement, AutomationElementAttribute> Clone()
    {
        return new AutomationElementNode(Parent, Element, FindVirtual) { _children = _children };
    }

    public override bool IsSamePosition(INode other) =>
        other switch
        {
            AutomationElementNode otherNode => Automation.CompareElements(Element, otherNode.Element),
            _ => false
        };

    IEnumerable<AutomationElementAttribute>? _properties = null;

    protected override IEnumerable<AutomationElementAttribute> GetProperties()
    {
        if (_properties == null)
        {
            Automation.PropertyIdAndName[] props =
            [
                new Automation.PropertyIdAndName(-1, "Role"),
                new Automation.PropertyIdAndName(-2, "ProcessName"),
                .. Automation.GetSupportedPropertyIdAndNames(Element)
            ];

            _properties = props.Select(x => new AutomationElementAttribute(x.Id, x.Name, GetPropertyValue)).ToList();
        }
        return _properties;
    }

    private object? GetPropertyValue(AutomationElementAttribute attribute)
    {
        try
        {
            if (attribute.Id == -1)
            {
                if (attribute.Name == "Role")
                    return Element.GetCurrentControlTypeName();

                return null;
            }
            else if (attribute.Id == -2)
            {
                if (attribute.Name == "ProcessName")
                {
                    return System.Diagnostics.Process.GetProcessById(Element.CurrentProcessId).ProcessName;
                }

                return null;
            }

            return Element.GetCurrentPropertyValueEx(attribute.Id, 0);
        }
        catch (Exception e)
        {
            return $"<Error>: {e.Message}";
        }
    }
}
