using System.Xml;
using System.Xml.XPath;
using PlatynUI.Technology.UiAutomation.Client;

namespace PlatynUI.Technology.UiAutomation.Core;

internal class XPathNavigator : System.Xml.XPath.XPathNavigator
{
    private object? _current;
    private bool _findVirtual;
    private XmlNameTable _nameTable;

    public XPathNavigator(
        IUIAutomationElement? element = null,
        bool findVirtual = false,
        XmlNameTable? nameTable = null
    )
    {
        element ??= Automation.RootElement;

        _findVirtual = findVirtual;

        _current = new AutomationElementNode(element, findVirtual);

        _nameTable = nameTable ?? new NameTable();
    }

    protected XPathNavigator(XPathNavigator other)
    {
        _current = other._current switch
        {
            INode node => node.Clone(),
            _ => throw new NotSupportedException(),
        };
        _nameTable = other._nameTable;
        _findVirtual = other._findVirtual;
    }

    public override string Value
    {
        get
        {
            return _current switch
            {
                IAttributesEnumerator enumerator => enumerator.Current.Value?.ToString() ?? string.Empty,
                _ => string.Empty,
            };
        }
    }

    public override object TypedValue
    {
        get
        {
            return _current switch
            {
                IAttributesEnumerator enumerator => enumerator.Current.Value!,
                _ => base.TypedValue,
            };
        }
    }
    public override XmlNameTable NameTable => _nameTable;

    public override XPathNodeType NodeType
    {
        get
        {
            return _current switch
            {
                INode node => node.Parent == null ? XPathNodeType.Root : XPathNodeType.Element,
                IAttributesEnumerator _ => XPathNodeType.Attribute,
                _ => XPathNodeType.All,
            };
        }
    }

    public override string LocalName
    {
        get
        {
            return _current switch
            {
                INode node => node.LocalName,
                IAttributesEnumerator enumerator => enumerator.Current.Name,
                _ => throw new NotSupportedException(),
            };
        }
    }

    public override string Name
    {
        get
        {
            var prefix = Prefix;
            if (string.IsNullOrEmpty(prefix))
            {
                return LocalName;
            }
            return $"{prefix}:{LocalName}";
        }
    }

    public override string NamespaceURI
    {
        get
        {
            return _current switch
            {
                INode node => node.NamespaceURI ?? string.Empty,
                IAttributesEnumerator enumerator => enumerator.Current.NamespaceURI,
                _ => string.Empty,
            };
        }
    }

    public override string Prefix
    {
        get
        {
            return _current switch
            {
                INode => LookupPrefix(NamespaceURI) ?? string.Empty,
                _ => string.Empty,
            };
        }
    }

    public override string BaseURI
    {
        get { return string.Empty; }
    }

    public override bool IsEmptyElement => false;

    public override object? UnderlyingObject =>
        _current switch
        {
            INode node => node.UnderlyingObject,
            IAttributesEnumerator enumerator => enumerator.Current.Value,
            _ => throw new NotSupportedException(),
        };

    public override System.Xml.XPath.XPathNavigator Clone()
    {
        return new XPathNavigator(this);
    }

    public override bool MoveToFirstAttribute()
    {
        switch (_current)
        {
            case INode node:
            {
                var enumerator = node.GetAttributesEnumerator();
                enumerator.Reset();

                if (!enumerator.MoveNext())
                {
                    return false;
                }

                _current = enumerator;

                return true;
            }
            default:
                return false;
        }
    }

    public override bool MoveToNextAttribute()
    {
        if (_current is IAttributesEnumerator enumerator)
        {
            return enumerator.MoveNext();
        }

        return false;
    }

    public override bool MoveToFirstNamespace(XPathNamespaceScope namespaceScope)
    {
        return false;
    }

    public override bool MoveToNextNamespace(XPathNamespaceScope namespaceScope)
    {
        return false;
    }

    public override bool MoveToNext()
    {
        switch (_current)
        {
            case INode node:
            {
                var sibling = node.GetNextSibling();
                if (sibling == null)
                {
                    return false;
                }

                _current = sibling;
                return true;
            }

            default:
                return false;
        }
    }

    public override bool MoveToPrevious()
    {
        switch (_current)
        {
            case INode node:
            {
                var sibling = node.GetPreviousSibling();
                if (sibling == null)
                {
                    return false;
                }

                _current = sibling;
                return true;
            }

            default:
                return false;
        }
    }

    public override bool MoveToFirstChild()
    {
        switch (_current)
        {
            case INode node:
            {
                var child = node.GetFirstChild();
                if (child == null)
                {
                    return false;
                }

                _current = child;
                return true;
            }

            default:
                return false;
        }
    }

    public override bool MoveToParent()
    {
        switch (_current)
        {
            case INode node:
            {
                var parent = node.Parent;
                if (parent == null)
                {
                    return false;
                }

                _current = parent;
                return true;
            }

            default:
                return false;
        }
    }

    public override bool MoveTo(System.Xml.XPath.XPathNavigator other)
    {
        if (other is XPathNavigator o)
        {
            _current = o._current;

            _nameTable = o._nameTable;
            _findVirtual = o._findVirtual;

            return true;
        }

        return false;
    }

    public override bool MoveToId(string id)
    {
        return false;
    }

    public override bool IsSamePosition(System.Xml.XPath.XPathNavigator other) =>
        other switch
        {
            XPathNavigator o when o._current is INode current && _current is INode current1
                => current.IsSamePosition(current1),
            XPathNavigator o => _current == o._current,
            _ => false,
        };

    public override string GetAttribute(string localName, string namespaceURI)
    {
        return base.GetAttribute(localName, namespaceURI);
    }
}
