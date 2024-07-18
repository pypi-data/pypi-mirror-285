using System.Collections;

namespace PlatynUI.Technology.UiAutomation.Core;

public interface IAttribute
{
    string Name { get; }
    object? Value { get; }
    string NamespaceURI { get; }
}

public interface IAttributesEnumerator : IEnumerator<IAttribute> { }

public interface INode
{
    object? UnderlyingObject { get; }

    INode? Parent { get; }

    bool FindVirtual { get; }

    INode? GetFirstChild();
    INode? GetLastChild();
    INode? GetNextSibling();
    INode? GetPreviousSibling();

    List<INode> Children { get; }

    string LocalName { get; }
    string NamespaceURI { get; }

    INode Clone();
    bool IsSamePosition(INode other);

    IAttributesEnumerator GetAttributesEnumerator();
}

public class AttributesEnumerator<T>(IEnumerable<T> properties) : IAttributesEnumerator
    where T : IAttribute
{
    private readonly IEnumerator<T> _enumerator = properties.GetEnumerator();

    public IAttribute Current => _enumerator.Current;

    object IEnumerator.Current => _enumerator.Current;

    public virtual void Dispose()
    {
        GC.SuppressFinalize(this);
        _enumerator.Dispose();
    }

    public bool MoveNext() => _enumerator.MoveNext();

    public void Reset() => _enumerator.MoveNext();
}

public abstract class Node<T, TAttr>(Node<T, TAttr>? parent, T element, bool findVirtual = false) : INode
    where TAttr : IAttribute
{
    public Node(T element, bool findVirtual = false)
        : this(null, element, findVirtual) { }

    INode? INode.Parent => Parent;

    public virtual Node<T, TAttr>? Parent { get; set; } = parent;

    public object? UnderlyingObject => Element;
    public virtual T Element { get; } = element;

    public bool FindVirtual { get; } = findVirtual;

    List<INode> INode.Children => Children.Cast<INode>().ToList();
    public abstract List<Node<T, TAttr>> Children { get; }

    public abstract string NamespaceURI { get; }

    public abstract string LocalName { get; }

    INode INode.Clone()
    {
        return Clone();
    }

    public abstract Node<T, TAttr> Clone();

    INode? INode.GetFirstChild()
    {
        return GetFirstChild();
    }

    public Node<T, TAttr>? GetFirstChild()
    {
        return Children.FirstOrDefault();
    }

    INode? INode.GetLastChild()
    {
        return GetLastChild();
    }

    public Node<T, TAttr>? GetLastChild()
    {
        return Children.LastOrDefault();
    }

    INode? INode.GetNextSibling()
    {
        return GetNextSibling();
    }

    public Node<T, TAttr>? GetNextSibling()
    {
        if (Parent == null)
            return default;

        var siblings = Parent.Children;
        int index = siblings.IndexOf(this);
        return (index >= 0 && index < siblings.Count - 1) ? siblings[index + 1] : null;
    }

    INode? INode.GetPreviousSibling()
    {
        return GetPreviousSibling();
    }

    public Node<T, TAttr>? GetPreviousSibling()
    {
        if (Parent == null)
            return null;

        var siblings = Parent.Children;
        int index = siblings.IndexOf(this);
        return (index > 0) ? siblings[index - 1] : null;
    }

    public abstract bool IsSamePosition(INode other);

    protected abstract IEnumerable<TAttr> GetProperties();

    IAttributesEnumerator INode.GetAttributesEnumerator()
    {
        return GetPropertiesEnumerator();
    }

    public virtual AttributesEnumerator<TAttr> GetPropertiesEnumerator()
    {
        return new AttributesEnumerator<TAttr>(GetProperties());
    }
}
