export default function IFramePage() {
    const component = "<div>hello</div>"
    return (
        <iframe src={"data:text/html;charset=utf-8," + encodeURIComponent(component)} width="100%" height="100%" title="hello" />
    );
}