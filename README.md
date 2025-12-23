# Review Manager

A streamlined code review management system designed to smooth up the review process within development teams.

## Overview

Review Manager helps teams organize and track code reviews efficiently, with built-in reward systems to encourage timely reviews and maintain team accountability.

## Key Features

### 📋 Review Workflow Management
- **My Todo**: Track reviews you need to complete and changes you need to address
- **Create Requests**: Submit new review requests with customizable priorities and reviewer assignments
- **Manage Requests**: Monitor all review requests you've created and their status

### 🎯 Flexible Review System
- **Review Priorities**:
  - Full Review: Complete code review with detailed feedback
  - Based on Evidence: Review based on test results and evidence
  - Approve Only: Quick approval, minimal review needed
- **Quick Reviews**: Fast-track reviews that have already been looked at once
- **Re-open Options**: Re-open approved tasks for quick checks or full re-reviews

### 🏆 Rewards & Motivation
- Track review completion and earn points
- Cycle-based reward tracking (weekly cycles starting Tuesday)
- Statistics dashboard showing your review contributions
- Leaderboards for most picked reviewers

### 📊 Smart Organization
- Automatic sorting by repository and PR number
- Lines of code estimation (1-99, 100-499, 500-1199, 1200+)
- Task states: Pending Review, Pending Changes, Approved
- Summary statistics for all your review activities

### 🔐 Authentication
- Google OAuth integration for secure team access
- User-specific dashboards and personalized views

## Tech Stack

### Frontend
- **React** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS v4** for modern, responsive UI
- **React Router** for navigation
- **Lucide React** for icons

### Backend
- Python/FastAPI (separate backend repository)
- RESTful API design
- Session-based authentication

## Project Structure

```
frontend/
├── src/
│   ├── api/           # API client and endpoint definitions
│   ├── components/    # Reusable React components
│   ├── contexts/      # React context providers (Auth)
│   ├── pages/         # Main page components
│   ├── types/         # TypeScript type definitions
│   └── App.tsx        # Main application component
├── public/            # Static assets
└── vite.config.ts     # Vite configuration
```

## Getting Started

### Prerequisites
- Node.js (v18 or higher)
- npm or yarn
- Backend API running (see backend repository)

### Installation

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Configure backend URL in `vite.config.ts` if needed

3. Start development server:
```bash
npm run dev
```

4. Open http://localhost:5173 in your browser

## Core Workflows

### For Reviewers
1. Check **My Todo → Pending Review** for new review requests
2. Review the PR on GitHub
3. Mark as **Approved** or **Request Changes**
4. Earn reward points for completed reviews

### For Request Creators
1. Use **Create New Request** to submit a PR for review
2. Select reviewers, set priority, and specify lines of code
3. Track progress in **Manage My Requests**
4. Address feedback in **My Todo → Pending Changes**
5. Re-open approved tasks if additional changes are needed

### Tracking Progress
- View earned rewards in **Rewards** section
- Filter by cycle to see historical performance
- Check summary statistics for insights

## Features in Detail

### Review Request Creation
- Paste GitHub PR link
- Choose review priority with descriptions
- Select lines of code category (automatically disables 1200+ for Full Reviews)
- Add multiple reviewers from team list
- See reviewer workload (time spent this cycle)

### Task Management
- View all assigned reviews in one place
- See creator, priority, lines of code, and reviewers at a glance
- Direct links to GitHub PRs
- Quick action buttons for workflow transitions
- Delete requests that are no longer needed

### Rewards System
- Points earned per review based on size and priority
- Weekly cycle tracking (Tuesday to Tuesday)
- Summary statistics: total reviews, breakdown by priority/size, top reviewers picked
- Historical data accessible for past cycles

## Contributing

This project is designed to make code reviews smoother, faster, and more rewarding for development teams. Feedback and contributions are welcome!
