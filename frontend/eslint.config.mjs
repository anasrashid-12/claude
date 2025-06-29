import eslintPluginNext from '@next/eslint-plugin-next';

/** @type {import('eslint').Linter.Config} */
export default [
  {
    ignores: ['**/node_modules/**', '**/.next/**'],
  },
  {
    rules: {},
    plugins: {
      '@next/next': eslintPluginNext,
    },
  },
];
