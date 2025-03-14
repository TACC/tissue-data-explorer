
var dagcomponentfuncs = window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {};

dagcomponentfuncs.dsLink = function (props) {
    if (!props.value) {
        return " "
    } else return React.createElement(window.dash_core_components.Link, {
        children: "View",
        href: props.value,
    });
}

dagcomponentfuncs.dsExternalLink = function (props) {
    if (props.value === " ") {
        return " "
    } else return React.createElement(window.dash_html_components.A, {
        children: "View",
        href: props.value,
    });
}

dagcomponentfuncs.previewImg = function (props) {
    if (props.value === " ") {
        return " "
    } else return React.createElement(
        'img',
        {
            src: props.value,
            class:"thumbnail"
            // onClick: onClick,
            // style: {height: '120px'},
        },
    );
}