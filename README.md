
# PlayRight - AI-Powered Sports Agency Platform

PlayRight is a comprehensive full-stack platform that connects athletes with local endorsement opportunities using advanced AI matching algorithms.

## 🏗️ Architecture

```
PlayRight/
├── 🎨 Frontend (React + TypeScript)
├── 🔧 API Server (FastAPI + Python)
├── 🤖 AI Engine (Machine Learning + NLP)
├── 📊 Database (PocketBase)
├── 🔄 Background Workers (Celery)
└── ⚡ Cache (Redis)
```

## ✨ Features

### 🤖 AI-Powered Matching
- **Smart Compatibility Scoring**: Multi-factor analysis including sport alignment, audience demographics, brand safety
- **Semantic Analysis**: NLP-powered profile matching using sentence transformers
- **Real-time Recommendations**: Dynamic matching based on user behavior and preferences
- **Market Insights**: Trending analysis and market saturation reports

### 👥 User Management
- **Role-based Authentication**: Athletes, Brands, and Agents with specific permissions
- **Profile Completion Tracking**: Guided onboarding with verification steps
- **Social Media Integration**: Automatic metrics syncing from major platforms
- **Real-time Notifications**: Email, push, and SMS notifications

### 💼 Deal Management
- **Campaign Creation**: Comprehensive campaign builder with targeting options
- **Deal Lifecycle**: From matching to completion with status tracking
- **Document Management**: Secure file uploads and contract storage
- **Analytics Dashboard**: Performance tracking and ROI analysis

### 📊 Advanced Analytics
- **User Analytics**: Individual performance metrics and insights
- **Market Analysis**: Sport-specific trends and opportunities
- **Platform Metrics**: Overall system health and usage statistics
- **Predictive Analytics**: Success rate predictions and recommendations

## 📋 Pages & Features

### Main Navigation
- **Home**: Dashboard with key metrics and overview
- **Player Search**: Search and filter player database
- **Deals**: Manage and track player contracts and deals
- **Market**: Market analysis and trends
- **News**: Latest sports industry news

### Account Features
- **Messages**: Internal communication system (coming soon)
- **Notifications**: Real-time alerts and updates (coming soon)
- **Profile**: User account management (coming soon)

## 🛠️ Tech Stack

- **Frontend Framework**: React 18
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI
- **Icons**: Lucide React
- **Build Tool**: Create React App
- **Package Manager**: npm

## 🚀 Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm (v8 or higher)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/playright-frontend.git
   cd playright-frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```

4. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

### Available Scripts

- `npm start` - Start the development server
- `npm build` - Build the app for production
- `npm test` - Run the test suite
- `npm eject` - Eject from Create React App (one-way operation)

## 🎨 Theme System

The application supports dynamic theme switching:

- **Light Mode**: Clean, bright interface
- **Dark Mode**: Easy on the eyes, professional look
- **System**: Automatically follows your OS preference

Toggle themes using the theme button in the header.

## 📱 Responsive Design

The application is fully responsive and optimized for:
- Desktop (1024px+)
- Tablet (768px - 1023px)
- Mobile (320px - 767px)

## 🏗️ Project Structure

```
src/
├── components/
│   ├── ui/           # Reusable UI components
│   ├── pages/        # Page components
│   ├── Layout.tsx    # Main layout component
│   ├── ThemeProvider.tsx
│   └── ThemeToggle.tsx
├── styles/
│   └── globals.css   # Global styles and CSS variables
├── App.tsx           # Main application component
└── index.tsx         # Application entry point
```

## 🎯 Key Components

### Layout System
- **Sidebar**: Collapsible navigation with smooth animations
- **Header**: Top navigation with theme toggle and user controls
- **Main Content**: Responsive content area

### UI Components
- **Button**: Multiple variants (default, secondary, ghost, destructive)
- **Card**: Content containers with consistent styling
- **Dropdown**: Context menus and navigation
- **Form Elements**: Inputs, selects, checkboxes, etc.

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory for environment-specific configuration:

```env
REACT_APP_API_URL=your_api_url_here
REACT_APP_ENVIRONMENT=development
```

### Tailwind Configuration
The project uses a custom Tailwind configuration with:
- Custom color palette
- Dark mode support
- Responsive breakpoints
- Custom animations

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

### Deploy to Vercel
1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel`

### Deploy to Netlify
1. Build the project: `npm run build`
2. Drag the `build` folder to Netlify

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Radix UI](https://www.radix-ui.com/) for accessible UI components
- [Tailwind CSS](https://tailwindcss.com/) for utility-first styling
- [Lucide React](https://lucide.dev/) for beautiful icons
- [Create React App](https://create-react-app.dev/) for the development setup

## 📞 Support

For support, email support@playright.ai or create an issue in this repository.

---

**PlayRight.ai** - Revolutionizing Sports Agency Management
