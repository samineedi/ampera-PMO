export function ItemLink({ item }) {
  return item.url ? <a href={item.url} target="_blank" rel="noopener noreferrer">{item.title}</a> : item.title;
}
