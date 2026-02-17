/**
 * HelixComponents Demo - Interactive Showcase
 * 
 * Copyright (c) 2024-2026 Kenneth Bingham
 * Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
 */

(function() {
    'use strict';
    
    var canvas, form, outputElement;
    var HC; // HelixComponents reference
    
    function init() {
        canvas = document.getElementById('form-canvas');
        outputElement = document.getElementById('form-output');
        
        if (!canvas) {
            console.error('Canvas not found!');
            return;
        }
        
        // Set canvas size
        canvas.width = 500;
        canvas.height = 520;
        
        // Get HelixComponents
        HC = window.HelixComponents;
        if (!HC) {
            console.error('HelixComponents not loaded!');
            return;
        }
        
        console.log('HelixComponents loaded:', Object.keys(HC));
        
        // Create the form
        createForm();
        
        // Start form rendering
        form.start();
        
        console.log('HelixComponents Demo initialized!');
    }
    
    function createForm() {
        form = new HC.HelixForm(canvas, {
            backgroundColor: { h: 230, s: 25, l: 10 }
        });
        
        // =========================================================================
        // PANEL 1: User Info
        // =========================================================================
        
        var userPanel = new HC.HelixPanel({
            id: 'user_panel',
            x: 20,
            y: 20,
            width: 460,
            height: 170,
            title: 'User Information',
            primaryColor: { h: 220, s: 70, l: 55 }
        });
        
        // Username field
        var usernameLabel = new HC.HelixLabel({
            x: 35,
            y: 75,
            text: 'Username',
            fontSize: 12,
            textColor: { h: 0, s: 0, l: 70 }
        });
        userPanel.addChild(usernameLabel);
        
        var usernameField = new HC.HelixTextField({
            id: 'username',
            x: 35,
            y: 95,
            width: 200,
            height: 36,
            placeholder: 'Enter username...',
            onChange: updateOutput
        });
        userPanel.addChild(usernameField);
        
        // Email field
        var emailLabel = new HC.HelixLabel({
            x: 250,
            y: 75,
            text: 'Email',
            fontSize: 12,
            textColor: { h: 0, s: 0, l: 70 }
        });
        userPanel.addChild(emailLabel);
        
        var emailField = new HC.HelixTextField({
            id: 'email',
            x: 250,
            y: 95,
            width: 215,
            height: 36,
            placeholder: 'user@example.com',
            onChange: updateOutput
        });
        userPanel.addChild(emailField);
        
        // Password field
        var passwordLabel = new HC.HelixLabel({
            x: 35,
            y: 140,
            text: 'Password',
            fontSize: 12,
            textColor: { h: 0, s: 0, l: 70 }
        });
        userPanel.addChild(passwordLabel);
        
        var passwordField = new HC.HelixTextField({
            id: 'password',
            x: 35,
            y: 160,
            width: 200,
            height: 36,
            placeholder: 'Enter password...',
            password: true,
            onChange: updateOutput
        });
        userPanel.addChild(passwordField);
        
        form.add(userPanel);
        
        // =========================================================================
        // PANEL 2: Settings
        // =========================================================================
        
        var settingsPanel = new HC.HelixPanel({
            id: 'settings_panel',
            x: 20,
            y: 205,
            width: 460,
            height: 180,
            title: 'Settings',
            primaryColor: { h: 280, s: 60, l: 55 }
        });
        
        // Volume slider
        var volumeLabel = new HC.HelixLabel({
            x: 35,
            y: 260,
            text: 'Volume',
            fontSize: 12,
            textColor: { h: 0, s: 0, l: 70 }
        });
        settingsPanel.addChild(volumeLabel);
        
        var volumeSlider = new HC.HelixSlider({
            id: 'volume',
            x: 35,
            y: 285,
            width: 200,
            min: 0,
            max: 100,
            value: 75,
            step: 1,
            primaryColor: { h: 280, s: 60, l: 55 },
            onChange: updateOutput
        });
        settingsPanel.addChild(volumeSlider);
        
        // Volume output
        var volumeOutput = new HC.HelixOutput({
            id: 'volume_display',
            x: 250,
            y: 275,
            width: 80,
            height: 30,
            value: '75',
            suffix: '%',
            primaryColor: { h: 280, s: 60, l: 55 }
        });
        settingsPanel.addChild(volumeOutput);
        
        // Connect slider to output
        volumeSlider.onChange = function(value) {
            volumeOutput.value = Math.round(value);
            updateOutput();
        };
        
        // Brightness slider
        var brightnessLabel = new HC.HelixLabel({
            x: 35,
            y: 320,
            text: 'Brightness',
            fontSize: 12,
            textColor: { h: 0, s: 0, l: 70 }
        });
        settingsPanel.addChild(brightnessLabel);
        
        var brightnessSlider = new HC.HelixSlider({
            id: 'brightness',
            x: 35,
            y: 345,
            width: 200,
            min: 0,
            max: 100,
            value: 50,
            step: 5,
            primaryColor: { h: 50, s: 80, l: 55 },
            onChange: updateOutput
        });
        settingsPanel.addChild(brightnessSlider);
        
        // Toggles
        var darkModeToggle = new HC.HelixToggle({
            id: 'dark_mode',
            x: 280,
            y: 260,
            width: 50,
            checked: true,
            label: 'Dark Mode',
            primaryColor: { h: 220, s: 70, l: 55 },
            onChange: updateOutput
        });
        settingsPanel.addChild(darkModeToggle);
        
        var notificationsToggle = new HC.HelixToggle({
            id: 'notifications',
            x: 280,
            y: 300,
            width: 50,
            checked: false,
            label: 'Notifications',
            primaryColor: { h: 140, s: 70, l: 45 },
            onChange: updateOutput
        });
        settingsPanel.addChild(notificationsToggle);
        
        var autoSaveToggle = new HC.HelixToggle({
            id: 'auto_save',
            x: 280,
            y: 340,
            width: 50,
            checked: true,
            label: 'Auto-Save',
            primaryColor: { h: 30, s: 80, l: 50 },
            onChange: updateOutput
        });
        settingsPanel.addChild(autoSaveToggle);
        
        form.add(settingsPanel);
        
        // =========================================================================
        // PANEL 3: Actions
        // =========================================================================
        
        var actionsPanel = new HC.HelixPanel({
            id: 'actions_panel',
            x: 20,
            y: 400,
            width: 460,
            height: 100,
            title: 'Actions',
            primaryColor: { h: 160, s: 60, l: 45 }
        });
        
        // Submit button
        var submitButton = new HC.HelixButton({
            id: 'submit',
            x: 35,
            y: 450,
            width: 130,
            height: 40,
            text: 'Submit',
            primaryColor: { h: 140, s: 70, l: 45 },
            onClick: function() {
                var values = form.getValues();
                console.log('Form submitted:', values);
                alert('Form Submitted!\n\n' + JSON.stringify(values, null, 2));
            }
        });
        actionsPanel.addChild(submitButton);
        
        // Reset button
        var resetButton = new HC.HelixButton({
            id: 'reset',
            x: 180,
            y: 450,
            width: 130,
            height: 40,
            text: 'Reset',
            primaryColor: { h: 220, s: 50, l: 50 },
            onClick: function() {
                form.setValues({
                    username: '',
                    email: '',
                    password: '',
                    volume: 75,
                    brightness: 50,
                    dark_mode: true,
                    notifications: false,
                    auto_save: true
                });
                volumeOutput.value = '75';
                updateOutput();
            }
        });
        actionsPanel.addChild(resetButton);
        
        // Cancel button
        var cancelButton = new HC.HelixButton({
            id: 'cancel',
            x: 325,
            y: 450,
            width: 130,
            height: 40,
            text: 'Cancel',
            primaryColor: { h: 0, s: 60, l: 50 },
            onClick: function() {
                console.log('Cancelled');
            }
        });
        actionsPanel.addChild(cancelButton);
        
        form.add(actionsPanel);
        
        // Initial output
        updateOutput();
    }
    
    function updateOutput() {
        if (form && outputElement) {
            var values = form.getValues();
            // Clean up - remove internal IDs
            var cleanValues = {};
            for (var key in values) {
                if (!key.includes('panel') && !key.includes('display')) {
                    cleanValues[key] = values[key];
                }
            }
            outputElement.textContent = JSON.stringify(cleanValues, null, 2);
        }
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();
