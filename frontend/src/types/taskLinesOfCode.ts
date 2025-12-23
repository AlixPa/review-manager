// Task lines of code enum matching backend
export enum TaskLinesOfCode {
  UNDER_100 = 1,
  UNDER_500 = 2,
  UNDER_1200 = 3,
  ABOVE_1200 = 4,
}

// Helper function to get display text
export const getTaskLinesOfCodeDisplay = (linesOfCode: number): string => {
  switch (linesOfCode) {
    case TaskLinesOfCode.UNDER_100:
      return '1~99';
    case TaskLinesOfCode.UNDER_500:
      return '100~499';
    case TaskLinesOfCode.UNDER_1200:
      return '500~1199';
    case TaskLinesOfCode.ABOVE_1200:
      return '1200+';
    default:
      return 'Unknown';
  }
};

