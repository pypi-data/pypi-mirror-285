using System.Xml.XPath;
using System.Xml.Xsl;

namespace PlatynUI.Technology.UiAutomation.Core;

public class XsltContext : System.Xml.Xsl.XsltContext
{
    public XsltContext()
        : base()
    {
        AddNamespace("", "http://platynui.io/raw");
        AddNamespace("raw", "http://platynui.io/raw");
        AddNamespace("native", "http://platynui.io/native");
        AddNamespace("element", "http://platynui.io/element");
        AddNamespace("item", "http://platynui.io/item");
        AddNamespace("app", "http://platynui.io/app");
    }

    public override bool HasNamespace(string prefix)
    {
        return base.HasNamespace(prefix);
    }

    public override string? LookupNamespace(string prefix)
    {
        var result = base.LookupNamespace(prefix);

        if (result == null)
        {
            result = "";
        }
        return result;
    }

    public override bool Whitespace => true;

    public override int CompareDocument(string baseUri, string nextbaseUri)
    {
        return string.CompareOrdinal(baseUri, nextbaseUri);
    }

    public override bool PreserveWhitespace(System.Xml.XPath.XPathNavigator node)
    {
        return false;
    }

    public override IXsltContextFunction ResolveFunction(string prefix, string name, XPathResultType[] ArgTypes)
    {
        if (name == "ends-with")
        {
            return endsWith;
        }

        return null!;
    }

    public override IXsltContextVariable ResolveVariable(string prefix, string name)
    {
        return null!;
    }

    internal readonly IXsltContextFunction endsWith = new UiaXsltFunctionEndsWith();

    internal class UiaXsltFunctionEndsWith : IXsltContextFunction
    {
        public int Minargs => 2;

        public int Maxargs => 2;

        public XPathResultType ReturnType => XPathResultType.Boolean;

        public XPathResultType[] ArgTypes => [XPathResultType.String, XPathResultType.String];

        public object Invoke(
            System.Xml.Xsl.XsltContext xsltContext,
            object[] args,
            System.Xml.XPath.XPathNavigator docContext
        )
        {
            if (args[0] is string s && args[1] is string suffix)
            {
                return s.EndsWith(suffix);
            }
            else if (args[0] is XPathNodeIterator nodeIterator && args[1] is string suffix1)
            {
                while (nodeIterator.MoveNext())
                {
                    if (nodeIterator.Current != null && nodeIterator.Current.Value.EndsWith(suffix1))
                    {
                        return true;
                    }
                }
            }

            return false;
        }
    }
}
