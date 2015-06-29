export function formatNumber(number) {
  return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}


export function humanizeNumber(number) {
  var millions = Math.round(number / 1000000);
  var formatted = millions.toString().replace(/(\d)(?=(\d{3})+$)/g, '$1.') + "M";
  return formatted;
}
