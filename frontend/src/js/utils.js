export function totalWords(wordsPerSource) {
  var total = 0;
  wordsPerSource.forEach(source => total += source.value);
  return total;
}


export function formatNumber(number) {
  var millions = Math.round(number / 1000000);
  var formatted = millions.toString().replace(/(\d)(?=(\d{3})+$)/g, '$1.') + "M";
  return formatted;
}
