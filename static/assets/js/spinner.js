function toggleSpinner(button, submitForm = false, keep = false) {
    const label = button.querySelector('.label');
    const spinner = button.querySelector('.spinner');
    let functionDef = button.getAttribute('data-function');
    console.log('functionDef:', functionDef);
    // Set a default function if data-function is not defined or empty
    if (!functionDef) {
        functionDef = 'resolve';
    }

    label.style.visibility = 'hidden'; // Make label invisible but keep its space
    spinner.style.visibility = 'visible'; // Show the spinner
    console.log('spinnerappear:', spinner);

    execute(functionDef).then(() => {
        console.log('function executed:', functionDef);
        if (submitForm && button.closest('form')) {
            return new Promise((resolve, reject) => {
                button.closest('form').submit();
                resolve();
            });
        }
    }).then(() => {
        if (!keep) {
            label.style.visibility = 'visible';
            spinner.style.visibility = 'hidden'; // Hide the spinner
            console.log('spinnerdisappear:', spinner);
        }
    }).catch((error) => {
        console.error(`Error in function ${functionDef}:`, error);
        label.style.visibility = 'visible';
        spinner.style.visibility = 'hidden'; // Hide the spinner
    });
}

function handleSubmit(event, submit = true, keep = true ) {
    event.preventDefault(); // Prevent default form submission
    const button = event.submitter;
    console.log('button function called');
    toggleSpinner(button, submit, keep);
}

function execute(str) {
    return new Promise((resolve, reject) => {
        console.log("executing:", str);
        try {
            if (typeof window[str] === 'function') {
                console.log("function found:", str);
                // If it's a function, call it and wait for it to complete
                const result = window[str]();
                if (result instanceof Promise) {
                    result.then(resolve).catch(reject);
                } else {
                    resolve(result);
                }
            } else {
                console.log("no function found:", str);
                // Otherwise, execute the string as code
                const result = eval(str);
                resolve(result);
            }
        } catch (error) {
            reject(error);
        }
    });
}
