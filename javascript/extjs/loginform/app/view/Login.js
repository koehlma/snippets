/*
 * Copyright (C) 2012, Maximilian Köhl <linuxmaxi@googlemail.com>
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 * 
 */

Ext.define('LoginForm.view.Login' ,{
    extend: 'Ext.container.Container',
    
    alias: 'widget.login',
    
    layout: 'absolute',   
    
    items: [{
        xtype: 'form',
        
        bodyPadding: 10,
        
        layout: 'form',
    
        width: 300,
        
        frame: true,
        
        url: '/request/login',
        
        defaultType: 'textfield',
        
        items: [{
            fieldLabel: 'Username',
            name: 'username',
            allowBlank: false,
            
            listeners: {
                render: function (field) {
                    field.focus(false, 250);
                },
                specialkey: function(field, e) {
                    if (e.getKey() === e.ENTER) {
                        var form = field.up('form');
                        form.login();
                    }
                }
            }            
        }, {
            fieldLabel: 'Password',
            inputType: 'password',
            name: 'password',
            allowBlank: false,
            
            listeners: {
                specialkey: function(field, e) {
                    if (e.getKey() === e.ENTER) {
                        var form = field.up('form');
                        form.login();
                    }
                }
            }                      
        }],
        
        login: function() {
            var form = this.getForm()
            
            if (form.isValid()) {
                var loading = new Ext.LoadMask(this, {});
                
                loading.show();
                
                form.submit({
                    success: function(form, action) {
                        form.owner.up('viewport').getLayout().next();
                        loading.destroy();
                    },
                    failure: function(form, action) {
                        loading.destroy();
                        var error = 'wrong username or password';
                        form.findField('username').markInvalid(error);
                        form.findField('password').markInvalid(error);
                    }
                });
            }
        },
        
        buttons: [{
            text: 'Login',
            formBind: true,
            disabled: true,
            
            handler: function(button) {            
                var form = button.up('form');
                                               
                form.login();
            }
        }] 
    }],
    
    listeners: {
        resize: function(component, width, height) {
            var form = component.down('form');
            var y = (height - form.getHeight()) / 2;
            var x = (width - form.getWidth()) / 2;
            form.setPosition(x, y)
        }
    }
});
