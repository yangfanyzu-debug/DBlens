type SqlToken = {
  value: string
  lower: string
  type: 'word' | 'identifier' | 'symbol'
  depth: number
}

const CLAUSE_BOUNDARIES = new Set([
  'where',
  'group',
  'order',
  'having',
  'limit',
  'offset',
  'fetch',
  'for',
  'procedure',
])

function isWordStart(char: string) {
  return /[A-Za-z_$]/.test(char)
}

function isWordPart(char: string) {
  return /[A-Za-z0-9_$]/.test(char)
}

function readQuoted(sql: string, start: number, quote: string) {
  let value = ''
  let i = start + 1
  while (i < sql.length) {
    const char = sql[i]
    const next = sql[i + 1]
    if (char === quote) {
      if (next === quote || (quote === '`' && next === '`')) {
        value += quote
        i += 2
        continue
      }
      return { value, end: i + 1 }
    }
    value += char
    i += 1
  }
  return { value, end: sql.length }
}

function tokenizeSql(sql: string): SqlToken[] {
  const tokens: SqlToken[] = []
  let i = 0
  let depth = 0

  while (i < sql.length) {
    const char = sql[i]
    const next = sql[i + 1]

    if (/\s/.test(char)) {
      i += 1
      continue
    }
    if (char === '-' && next === '-') {
      i = sql.indexOf('\n', i + 2)
      if (i < 0) break
      continue
    }
    if (char === '#') {
      i = sql.indexOf('\n', i + 1)
      if (i < 0) break
      continue
    }
    if (char === '/' && next === '*') {
      const end = sql.indexOf('*/', i + 2)
      i = end < 0 ? sql.length : end + 2
      continue
    }
    if (char === "'") {
      i = readQuoted(sql, i, "'").end
      continue
    }
    if (char === '`' || char === '"') {
      const quoted = readQuoted(sql, i, char)
      tokens.push({ value: quoted.value, lower: quoted.value.toLowerCase(), type: 'identifier', depth })
      i = quoted.end
      continue
    }
    if (char === '(') {
      tokens.push({ value: char, lower: char, type: 'symbol', depth })
      depth += 1
      i += 1
      continue
    }
    if (char === ')') {
      depth = Math.max(0, depth - 1)
      tokens.push({ value: char, lower: char, type: 'symbol', depth })
      i += 1
      continue
    }
    if (',.;'.includes(char)) {
      tokens.push({ value: char, lower: char, type: 'symbol', depth })
      i += 1
      continue
    }
    if (isWordStart(char)) {
      let end = i + 1
      while (end < sql.length && isWordPart(sql[end])) end += 1
      const value = sql.slice(i, end)
      tokens.push({ value, lower: value.toLowerCase(), type: 'word', depth })
      i = end
      continue
    }

    i += 1
  }

  return tokens
}

function readTablePath(tokens: SqlToken[], start: number) {
  const parts: string[] = []
  let i = start

  if (!tokens[i] || !['word', 'identifier'].includes(tokens[i].type)) return null
  parts.push(tokens[i].value)
  i += 1

  while (
    tokens[i]?.value === '.'
    && tokens[i + 1]
    && ['word', 'identifier'].includes(tokens[i + 1].type)
  ) {
    parts.push(tokens[i + 1].value)
    i += 2
  }

  return { table: parts.join('.'), nextIndex: i }
}

export function inferSingleSelectTableName(sql: string): string | null {
  const tokens = tokenizeSql(sql)
  const firstTopLevelWord = tokens.find(token => token.depth === 0 && token.type === 'word')
  if (!firstTopLevelWord || firstTopLevelWord.lower !== 'select') return null
  if (tokens.some(token => token.depth === 0 && token.lower === 'with')) return null
  if (tokens.some(token => token.depth === 0 && token.lower === 'union')) return null

  const fromIndex = tokens.findIndex(token => token.depth === 0 && token.lower === 'from')
  if (fromIndex < 0) return null
  if (tokens[fromIndex + 1]?.value === '(') return null

  const target = readTablePath(tokens, fromIndex + 1)
  if (!target) return null

  for (let i = target.nextIndex; i < tokens.length; i += 1) {
    const token = tokens[i]
    if (token.depth !== 0) continue
    if (CLAUSE_BOUNDARIES.has(token.lower)) break
    if (token.value === ',' || token.lower.endsWith('join')) return null
  }

  return target.table
}
