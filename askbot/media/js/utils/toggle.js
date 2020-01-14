var Toggle = function() {
    this._state = 'off-state';
    this._messages = {};
    this._states = [
        'on-state',
        'off-state',
        'on-prompt',
        'off-prompt'
    ];
};
inherits(Toggle, SimpleControl);

Toggle.prototype.resetStyles = function () {
    var element = this._element;
    var states = this._states;
    $.each(states, function (idx, state) {
        element.removeClass(state);
    });
    this.setText('');
};

Toggle.prototype.isOn = function () {
    return this._element.data('isOn');
};

Toggle.prototype.isCheckBox = function () {
    var element = this._element;
    return element.attr('type') === 'checkbox';
};

Toggle.prototype.setState = function (state) {
    var element = this._element;
    var oldState = this._state;
    this._state = state;
    if (element) {
        this.resetStyles();
        element.addClass(state);
        if (state === 'on-state') {
            element.data('isOn', true);
        } else if (state === 'off-state') {
            element.data('isOn', false);
        }
        if (this.isCheckBox()) {
            if (state === 'on-state') {
                element.attr('checked', true);
            } else if (state === 'off-state') {
                element.attr('checked', false);
            }
        } else {
            this.setText(this._messages[state]);
        }
        this._element.trigger(
            'askbot.Toggle.stateChange',
            {'oldState': oldState, 'newState': state}
        );
    }
};

Toggle.prototype.toggleState = function () {
    if (this.isOn()) {
        this.setState('off-state');
    } else {
        this.setState('on-state');
    }
};

Toggle.prototype.setText = function (text) {
    var btnText = this._element.find('.js-btn-text');
    var where  = btnText.length ? btnText : this._element;
    where.html(text);
};

Toggle.prototype.setMessages = function(messages) {
    $.extend(this._messages, messages);
};

Toggle.prototype.setMessage = function(state, text) {
    this._messages[state] = text;
};

Toggle.prototype.createDom = function () {
    //limitation is that we make a div with createDom
    var element = this.makeElement('div');
    this._element = element;

    var messages = this._messages || {};

    messages['on-state'] = messages['on-state'] || gettext('enabled');
    messages['off-state'] = messages['off-state'] || gettext('disabled');

    element.data('onStateText', messages['on-state']);
    element.data('offStateText', messages['off-state']);
    element.data('onPromptText', messages['on-prompt'] || messages['off-state']);
    element.data('offPromptText', messages['off-prompt'] || messages['on-state']);

    this.decorate(element);
};

Toggle.prototype.decorate = function (element) {
    this._element = element;
    //read messages for all states
    var messages = {};
    messages['on-state'] = element.data('onStateText') || gettext('enabled');
    messages['off-state'] = element.data('offStateText') || gettext('disabled');
    messages['on-prompt'] = element.data('onPromptText') || messages['off-state'];
    messages['off-prompt'] = element.data('offPromptText') || messages['on-state'];
    this._messages = messages;


    //detect state and save it
    if (this.isCheckBox()) {
        this._state = this._state || (element.is(':checked') ? 'on-state' : 'off-state');
    } else {
        this._state = element.data('isOn') ? 'on-state' : this._state;
    }
    this.setState(this._state);

    //set mouseover handler only for non-checkbox version
    if (this.isCheckBox() === false) {
        var me = this;
        element.mouseover(function () {
            var is_on = me.isOn();
            if (is_on) {
                me.setState('off-prompt');
            } else {
                me.setState('on-prompt');
            }
            return false;
        });
        element.mouseout(function () {
            var is_on = me.isOn();
            if (is_on) {
                me.setState('on-state');
            } else {
                me.setState('off-state');
            }
            return false;
        });
    }

    setupButtonEventHandlers(element, this.getHandler());
};


function toggle_display(button, id, hiddenText, visibleText) {
    element = document.getElementById(id);
    if (element.style.display == "block"){
        element.style.display = "none";
        button.innerText = hiddenText
    }
    else {
        element.style.display = "block";
        button.innerText = visibleText
    }
}


function toggle_mode(element){
    console.log(element.value);
    translation_text = document.getElementsByClassName("ask-form--editor-container")[0];
    translation_text_text_area = document.getElementById("editor");
    advanced_options = document.getElementById("advanced_options");
    toggle_button = document.getElementById("toggle_button");
    toggle_input = document.getElementById("toggle-input");

    if (element.value == "quick_mode"){
        translation_text.style.display = "block";
        advanced_options.style.display = "none";
    }
    else if (element.value == "contract_mode") {
        translation_text.style.display = "none";
        advanced_options.style.display = "block";
        toggle_input.style.display = "block";
        toggle_button.innerText = 'Hide details field';
        translation_text_text_area.value = " ";
    }
}
