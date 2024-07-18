namespace PlatynUI.Technology.UiAutomation.Core;

using System.Collections.Generic;

internal class ElementNavigatorBase
{
    public virtual string NamespaceURI { get; set; } = "http://platynui.io/raw";
}

internal abstract class ElementNavigatorBase<TParent, TChild>(TParent? parent) : ElementNavigatorBase
{
    public TParent? Parent { get; protected set; } = parent;

    public int CurrentIndex { get; protected set; }

    protected abstract IReadOnlyList<TChild> Children { get; }

    public bool IsStarted { get; protected set; }

    public void Reset()
    {
        IsStarted = false;
        CurrentIndex = -1;
    }

    public virtual TChild? Current
    {
        get
        {
            if (IsStarted && CurrentIndex < Children.Count)
            {
                return Children[CurrentIndex];
            }

            return default;
        }
    }

    public virtual bool MoveToFirst()
    {
        IsStarted = true;

        if (Children.Count <= 0)
        {
            return false;
        }

        CurrentIndex = 0;

        return true;
    }



    public bool MoveToNext()
    {
        if (IsStarted && CurrentIndex + 1 >= Children.Count)
        {
            return false;
        }

        CurrentIndex++;

        return true;
    }

    public bool MoveToPrevious()
    {
        if (IsStarted && CurrentIndex - 1 < 0)
        {
            return false;
        }

        CurrentIndex--;

        return true;
    }

    public abstract ElementNavigatorBase<TParent, TChild> Clone();
}
