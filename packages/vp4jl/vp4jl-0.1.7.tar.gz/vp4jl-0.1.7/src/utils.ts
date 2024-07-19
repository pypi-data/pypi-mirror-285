export function isSameContent(
  a: string | null | object | undefined,
  b: string | null | object | undefined
): boolean {
  const pureContentString = (content: string | null | object | undefined) => {
    let pure = content;
    if (typeof content === 'string') {
      pure = JSON.parse(content || 'null');
    }
    return JSON.stringify(pure);
  };
  const aContent = pureContentString(a);
  const bContent = pureContentString(b);
  return aContent === bContent;
}
