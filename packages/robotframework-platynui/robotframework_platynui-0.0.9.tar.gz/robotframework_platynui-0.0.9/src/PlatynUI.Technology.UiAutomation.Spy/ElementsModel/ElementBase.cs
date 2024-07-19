using System.Collections;
using System.Collections.ObjectModel;
using System.Collections.Specialized;
using Caliburn.Micro;

namespace PlatynUI.Technology.UiAutomation.Spy.ElementsModel;

public class PropertyEntry
{
    public virtual string? Name { get; set; } = null;
    public virtual object? Value { get; set; }
}

public abstract class ElementBase(ElementBase? parent)
    : PropertyChangedBase,
        IHaveDisplayName,
        IChild<ElementBase?>,
        IParent<ElementBase?>,
        IEnumerable<ElementBase>
{
    private ObservableCollection<ElementBase>? _children;
    private ObservableCollection<ElementBase>? _oldChildren;

    private string? _iconSource;
    private bool _isExpanded;
    private bool _isSelected;
    private ElementBase? _parent = parent;

    private ObservableCollection<PropertyEntry>? _properties;

    public bool IsSelected
    {
        get => _isSelected;
        set
        {
            if (value == _isSelected)
            {
                return;
            }

            _isSelected = value;
            NotifyOfPropertyChange();
        }
    }

    public bool IsExpanded
    {
        get => _isExpanded;
        set
        {
            if (value == _isExpanded)
            {
                return;
            }

            _isExpanded = value;
            NotifyOfPropertyChange();
        }
    }

    public string? IconSource
    {
        get => _iconSource;
        set
        {
            if (value == _iconSource)
            {
                return;
            }

            _iconSource = value;
            NotifyOfPropertyChange();
        }
    }

    public ICollection<ElementBase> Children
    {
        get
        {
            if (_children == null)
            {
                _children = InitChildren();

                _children.CollectionChanged += ChildrenOnCollectionChanged!;
            }

            return _children;
        }
    }

    public ICollection<ElementBase>? OldChildren
    {
        get
        {

            return _oldChildren;
        }
    }

    public virtual ICollection<PropertyEntry> Properties => _properties ??= InitProperties();

    object? IChild.Parent
    {
        get => Parent;
        set => Parent = value as ElementBase;
    }

    public ElementBase? Parent
    {
        get => _parent;
        set
        {
            if (Equals(value, _parent))
            {
                return;
            }

            _parent?._children?.Remove(this);
            _parent = value;
            if (!_parent?._children?.Contains(this) ?? false)
            {
                _parent?._children?.Add(this);
            }

            NotifyOfPropertyChange();
        }
    }

    public IEnumerator<ElementBase> GetEnumerator()
    {
        return Children.GetEnumerator();
    }

    IEnumerator IEnumerable.GetEnumerator()
    {
        return GetEnumerator();
    }

    private string? _displayName;

    public virtual string DisplayName
    {
        get => _displayName ??= InitDisplayName();
        set
        {
            if (value == _displayName)
            {
                return;
            }

            _displayName = value;
            NotifyOfPropertyChange();
        }
    }

    protected virtual string InitDisplayName()
    {
        return "";
    }

    private string? _fullDisplayName;

    protected virtual string InitFullDisplayName()
    {
        return "";
    }

    public virtual string FullDisplayName
    {
        get => _fullDisplayName ??= InitFullDisplayName();
        set
        {
            if (value == _fullDisplayName)
            {
                return;
            }

            _fullDisplayName = value;
            NotifyOfPropertyChange();
        }
    }

    public IEnumerable<ElementBase> GetChildren()
    {
        return Children;
    }

    IEnumerable IParent.GetChildren()
    {
        return GetChildren();
    }

    private void ChildrenOnCollectionChanged(object sender, NotifyCollectionChangedEventArgs args)
    {
        switch (args.Action)
        {
            case NotifyCollectionChangedAction.Add:

                foreach (var v in args.NewItems!.OfType<ElementBase>())
                {
                    if (v != null)
                    {
                        v.Parent = this;
                    }
                }

                break;
            case NotifyCollectionChangedAction.Remove:

                foreach (var v in args.OldItems!.OfType<ElementBase>())
                {
                    if (v != null && v.Parent == this)
                    {
                        v.Parent = null;
                    }
                }

                break;
        }
    }

    protected virtual ObservableCollection<ElementBase> InitChildren()
    {
        return [];
    }

    protected virtual ObservableCollection<PropertyEntry> InitProperties()
    {
        return [];
    }

    public override void Refresh()
    {
        _properties = null;

        _oldChildren = _children;
        _children = null;

        base.Refresh();
    }
}
