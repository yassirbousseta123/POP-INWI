import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';
import eslintConfigPrettier from 'eslint-config-prettier'; // Import prettier config

export default tseslint.config(
  eslint.configs.recommended,
  ...tseslint.configs.recommended, // Basic recommended rules - Apply broadly
  {
    // Global ignores
    ignores: [
      'node_modules/',
      'build/',
      'dist/', // Add dist
      'coverage/', // Add coverage
      'docs/.vitepress/cache/', // Ignore vitepress cache
      'docs/.vitepress/dist/', // Ignore vitepress build output
      'eslint.config.js',
    ],
  },
  // Configuration specific to TypeScript files, including type-aware rules
  ...tseslint.config({
    files: ['**/*.ts'],
    extends: [
      ...tseslint.configs.strictTypeChecked, // Apply strictest type-aware rules ONLY to TS files
      ...tseslint.configs.stylisticTypeChecked, // Apply stylistic rules requiring TS config
    ],
    languageOptions: {
      parserOptions: {
        project: './tsconfig.eslint.json', // Point to specific tsconfig for ESLint
        tsconfigRootDir: import.meta.dirname,
      },
    },
    rules: {
      // General JS/TS Rules (applied within TS context)
      'no-console': ['warn', { allow: ['warn', 'error', 'info'] }],
      'prefer-const': 'error',
      eqeqeq: ['error', 'always'],
      'no-unused-vars': 'off', // Use TS version
      complexity: ['error', { max: 10 }],
      'max-lines': ['warn', { max: 300, skipBlankLines: true, skipComments: true }],
      'max-lines-per-function': ['warn', { max: 50, skipBlankLines: true, skipComments: true }],
      'max-depth': ['warn', 3],
      'max-params': ['warn', 4],

      // TypeScript Specific Rules (override/add)
      '@typescript-eslint/no-unused-vars': [
        'error',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_' },
      ],
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/explicit-function-return-type': 'error',
      '@typescript-eslint/no-non-null-assertion': 'error',
      '@typescript-eslint/no-use-before-define': 'error',
      '@typescript-eslint/no-floating-promises': 'error',
      '@typescript-eslint/consistent-type-imports': 'error',
      '@typescript-eslint/no-misused-promises': 'error',
      '@typescript-eslint/prefer-readonly': 'warn',
    },
  }),
  {
    // Configuration for specific files to relax rules
    files: [
      'src/handlers/readPdf.ts',
      'test/**/*.ts', // Includes .test.ts and .bench.ts
    ],
    rules: {
      complexity: 'off',
      'max-lines': 'off',
      'max-lines-per-function': 'off',
      'max-depth': 'off', // Also disable max-depth for these complex files/tests
      '@typescript-eslint/no-unsafe-call': 'warn', // Downgrade unsafe-call to warning for tests if needed
      '@typescript-eslint/no-unsafe-assignment': 'warn', // Downgrade related rule
      '@typescript-eslint/no-unsafe-member-access': 'warn', // Downgrade related rule
    },
  },
  {
    // Configuration for JavaScript files (CommonJS like config files)
    files: ['**/*.js', '**/*.cjs'], // Include .cjs files
    languageOptions: {
      globals: {
        module: 'readonly', // Define CommonJS globals
        require: 'readonly',
        process: 'readonly',
        __dirname: 'readonly',
      },
    },
    rules: {
      // Add JS/CJS specific rules if needed
      '@typescript-eslint/no-var-requires': 'off', // Allow require in CJS if needed
    },
  },
  eslintConfigPrettier // Add prettier config last to override other formatting rules
);
