

# PlayRight.ai - Sports Agency Platform

A modern, responsive web application for sports agency management, built with React, TypeScript, and Tailwind CSS.

## 🚀 Features

- **Modern UI/UX**: Clean, professional interface with dark/light theme support
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **TypeScript**: Full type safety and better development experience
- **Tailwind CSS**: Utility-first CSS framework for rapid styling
- **Component Library**: Comprehensive UI components built with Radix UI
- **Theme System**: Dynamic dark/light mode switching
- **Collapsible Sidebar**: Space-efficient navigation with smooth animations

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
