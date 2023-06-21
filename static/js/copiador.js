function CopyText(num) {
var text = document.getElementById(num)
text.select();
navigator.clipboard.writeText(text.value);
}