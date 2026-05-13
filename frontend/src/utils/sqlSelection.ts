export function getSqlToExecute(selectedSql: string | null | undefined, fullSql: string): string {
  return selectedSql?.trim() ? selectedSql : fullSql
}
