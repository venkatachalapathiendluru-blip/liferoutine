class User {
    constructor(id, username, email, role = 'USER', isActive = true) {
        this.id = id;
        this.username = username;
        this.email = email;
        this.role = role; // USER or ADMIN
        this.isActive = isActive;
        this.createdAt = new Date().toISOString();
        this.lastLogin = null;
    }
    
    static ROLES = {
        USER: 'USER',
        ADMIN: 'ADMIN'
    };
    
    hasRole(role) {
        return this.role === role;
    }
    
    isAdmin() {
        return this.role === User.ROLES.ADMIN;
    }
    
    toJSON() {
        return {
            id: this.id,
            username: this.username,
            email: this.email,
            role: this.role,
            isActive: this.isActive,
            createdAt: this.createdAt,
            lastLogin: this.lastLogin
        };
    }
    
    static fromJSON(data) {
        const user = new User(data.id, data.username, data.email, data.role, data.isActive);
        user.createdAt = data.createdAt;
        user.lastLogin = data.lastLogin;
        return user;
    }
}

class Module {
    constructor(id, name, description, category = 'general', isEnabled = true, requiredRole = 'USER') {
        this.id = id;
        this.name = name;
        this.description = description;
        this.category = category;
        this.isEnabled = isEnabled;
        this.requiredRole = requiredRole;
        this.createdAt = new Date().toISOString();
    }
    
    static CATEGORIES = {
        NUTRITION: 'nutrition',
        HYDRATION: 'hydration',
        ROUTINE: 'routine',
        ADMIN: 'admin',
        ANALYTICS: 'analytics'
    };
    
    isAccessibleBy(user) {
        if (!this.isEnabled) return false;
        if (this.requiredRole === Module.REQUIRED_ROLES.ADMIN && !user.isAdmin()) return false;
        return true;
    }
    
    static REQUIRED_ROLES = {
        USER: 'USER',
        ADMIN: 'ADMIN'
    };
    
    toJSON() {
        return {
            id: this.id,
            name: this.name,
            description: this.description,
            category: this.category,
            isEnabled: this.isEnabled,
            requiredRole: this.requiredRole,
            createdAt: this.createdAt
        };
    }
    
    static fromJSON(data) {
        const module = new Module(data.id, data.name, data.description, data.category, data.isEnabled, data.requiredRole);
        module.createdAt = data.createdAt;
        return module;
    }
}

class AuthManager {
    constructor() {
        this.currentUser = null;
        this.users = [];
        this.modules = [];
        this.sessionTimeout = 24 * 60 * 60 * 1000; // 24 hours
        this.init();
    }
    
    init() {
        this.loadUsers();
        this.loadModules();
        this.loadCurrentSession();
        this.initializeDefaultData();
    }
    
    initializeDefaultData() {
        // Create default admin user if none exists
        if (this.users.length === 0) {
            this.createUser('admin', 'admin@liferoutine.com', 'admin123', User.ROLES.ADMIN);
        }
        
        // Create default modules if none exist
        if (this.modules.length === 0) {
            this.createDefaultModules();
        }
    }
    
    createDefaultModules() {
        const defaultModules = [
            new Module('meal-planner', 'Meal Planner', 'Plan and track daily meals', Module.CATEGORIES.NUTRITION, true, User.ROLES.USER),
            new Module('water-tracker', 'Water Tracker', 'Track daily water intake', Module.CATEGORIES.HYDRATION, true, User.ROLES.USER),
            new Module('daily-summary', 'Daily Summary', 'View end-of-day health summary', Module.CATEGORIES.ANALYTICS, true, User.ROLES.USER),
            new Module('food-management', 'Food Management', 'Admin food and ingredient management', Module.CATEGORIES.ADMIN, true, User.ROLES.ADMIN),
            new Module('module-management', 'Module Management', 'Enable/disable application features', Module.CATEGORIES.ADMIN, true, User.ROLES.ADMIN),
            new Module('user-management', 'User Management', 'Manage application users', Module.CATEGORIES.ADMIN, false, User.ROLES.ADMIN),
            new Module('advanced-analytics', 'Advanced Analytics', 'Detailed health analytics and reports', Module.CATEGORIES.ANALYTICS, false, User.ROLES.USER),
            new Module('routine-engine', 'Routine Engine', 'Generate personalized daily routines', Module.CATEGORIES.ROUTINE, true, User.ROLES.USER)
        ];
        
        defaultModules.forEach(module => {
            this.modules.push(module);
        });
        
        this.saveModules();
    }
    
    // User Management
    createUser(username, email, password, role = User.ROLES.USER) {
        if (this.getUserByUsername(username)) {
            throw new Error('Username already exists');
        }
        
        if (this.getUserByEmail(email)) {
            throw new Error('Email already exists');
        }
        
        const user = new User(
            this.generateId(),
            username,
            email,
            role
        );
        
        user.passwordHash = this.hashPassword(password);
        
        this.users.push(user);
        this.saveUsers();
        
        return user;
    }
    
    authenticateUser(username, password) {
        const user = this.getUserByUsername(username);
        
        if (!user || !user.isActive) {
            throw new Error('Invalid username or password');
        }
        
        if (!this.verifyPassword(password, user.passwordHash)) {
            throw new Error('Invalid username or password');
        }
        
        // Update last login
        user.lastLogin = new Date().toISOString();
        this.saveUsers();
        
        return user;
    }
    
    login(username, password) {
        const user = this.authenticateUser(username, password);
        this.currentUser = user;
        this.sessionStart = Date.now();
        this.saveCurrentSession();
        
        return user;
    }
    
    logout() {
        this.currentUser = null;
        this.sessionStart = null;
        this.clearCurrentSession();
    }
    
    isLoggedIn() {
        return this.currentUser !== null && this.sessionStart && (Date.now() - this.sessionStart < this.sessionTimeout);
    }
    
    isSessionExpired() {
        return this.sessionStart && (Date.now() - this.sessionStart >= this.sessionTimeout);
    }
    
    getCurrentUser() {
        if (this.isSessionExpired()) {
            this.logout();
            return null;
        }
        return this.currentUser;
    }
    
    requireAuth() {
        if (!this.isLoggedIn()) {
            throw new Error('Authentication required');
        }
    }
    
    requireRole(requiredRole) {
        this.requireAuth();
        if (requiredRole === User.ROLES.ADMIN && !this.currentUser.isAdmin()) {
            throw new Error('Admin access required');
        }
    }
    
    // Module Management
    getModules(category = null) {
        let modules = this.modules;
        
        if (category) {
            modules = modules.filter(module => module.category === category);
        }
        
        return modules;
    }
    
    getModule(id) {
        return this.modules.find(module => module.id === id);
    }
    
    toggleModule(id) {
        const module = this.getModule(id);
        if (module) {
            module.isEnabled = !module.isEnabled;
            this.saveModules();
            return module;
        }
        return null;
    }
    
    updateModule(id, updates) {
        const module = this.getModule(id);
        if (module) {
            Object.assign(module, updates);
            this.saveModules();
            return module;
        }
        return null;
    }
    
    isModuleEnabled(moduleId) {
        const module = this.getModule(moduleId);
        if (!module || !this.isLoggedIn()) {
            return false;
        }
        
        return module.isAccessibleBy(this.currentUser);
    }
    
    getEnabledModules() {
        if (!this.isLoggedIn()) {
            return [];
        }
        
        return this.modules.filter(module => module.isAccessibleBy(this.currentUser));
    }
    
    // User Management (Admin only)
    getUserById(id) {
        return this.users.find(user => user.id === id);
    }
    
    getUserByUsername(username) {
        return this.users.find(user => user.username === username);
    }
    
    getUserByEmail(email) {
        return this.users.find(user => user.email === email);
    }
    
    getAllUsers() {
        return this.users;
    }
    
    updateUser(id, updates) {
        const user = this.getUserById(id);
        if (user) {
            Object.assign(user, updates);
            this.saveUsers();
            return user;
        }
        return null;
    }
    
    toggleUserStatus(id) {
        const user = this.getUserById(id);
        if (user) {
            user.isActive = !user.isActive;
            this.saveUsers();
            return user;
        }
        return null;
    }
    
    // Utility methods
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }
    
    hashPassword(password) {
        // Simple hash for demo - in production, use proper password hashing
        return btoa(password + 'liferoutine_salt');
    }
    
    verifyPassword(password, hash) {
        return this.hashPassword(password) === hash;
    }
    
    // Data persistence
    saveUsers() {
        const userData = this.users.map(user => user.toJSON());
        localStorage.setItem('liferoutine_users', JSON.stringify(userData));
    }
    
    loadUsers() {
        const userData = localStorage.getItem('liferoutine_users');
        if (userData) {
            try {
                this.users = JSON.parse(userData).map(user => User.fromJSON(user));
            } catch (error) {
                console.error('Error loading users:', error);
                this.users = [];
            }
        }
    }
    
    saveModules() {
        const moduleData = this.modules.map(module => module.toJSON());
        localStorage.setItem('liferoutine_modules', JSON.stringify(moduleData));
    }
    
    loadModules() {
        const moduleData = localStorage.getItem('liferoutine_modules');
        if (moduleData) {
            try {
                this.modules = JSON.parse(moduleData).map(module => Module.fromJSON(module));
            } catch (error) {
                console.error('Error loading modules:', error);
                this.modules = [];
            }
        }
    }
    
    saveCurrentSession() {
        if (this.currentUser) {
            const sessionData = {
                user: this.currentUser.toJSON(),
                sessionStart: this.sessionStart
            };
            localStorage.setItem('liferoutine_session', JSON.stringify(sessionData));
        }
    }
    
    loadCurrentSession() {
        const sessionData = localStorage.getItem('liferoutine_session');
        if (sessionData) {
            try {
                const session = JSON.parse(sessionData);
                this.currentUser = User.fromJSON(session.user);
                this.sessionStart = session.sessionStart;
                
                // Check if session is expired
                if (this.isSessionExpired()) {
                    this.logout();
                }
            } catch (error) {
                console.error('Error loading session:', error);
                this.clearCurrentSession();
            }
        }
    }
    
    clearCurrentSession() {
        localStorage.removeItem('liferoutine_session');
        this.currentUser = null;
        this.sessionStart = null;
    }
}

// Global auth manager instance
const authManager = new AuthManager();