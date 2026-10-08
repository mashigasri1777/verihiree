/**
 * VERIRESUME - Client-Side Application JavaScript
 * Handles drag-and-drop upload, verification pipeline modal, and dynamic API interactions.
 */

document.addEventListener("DOMContentLoaded", () => {
    initUploadPage();
});

/* ==========================================================================
   1. Resume Upload Page Handler
   ========================================================================== */
function initUploadPage() {
    const dropZone = document.getElementById("dropZone");
    const fileInput = document.getElementById("resumeFileInput");
    const fileInfo = document.getElementById("fileSelectedInfo");
    const fileName = document.getElementById("selectedFileName");
    const fileSize = document.getElementById("selectedFileSize");
    const fileIcon = document.getElementById("fileTypeIcon");
    const removeBtn = document.getElementById("removeFileBtn");
    const submitBtn = document.getElementById("uploadSubmitBtn");
    const uploadForm = document.getElementById("resumeUploadForm");
    const progressContainer = document.getElementById("progressContainer");
    const progressBarFill = document.getElementById("progressBarFill");
    const progressStatusText = document.getElementById("progressStatusText");
    const progressPercent = document.getElementById("progressPercent");

    if (!dropZone || !fileInput) return;

    // Drag & Drop Listeners
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add("dragover");
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove("dragover");
        }, false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });

    // File Input change
    fileInput.addEventListener('change', (e) => {
        if (fileInput.files.length > 0) {
            handleFileSelect(fileInput.files[0]);
        }
    });

    // Remove file button
    if (removeBtn) {
        removeBtn.addEventListener('click', () => {
            fileInput.value = "";
            fileInfo.style.display = "none";
            dropZone.style.display = "block";
            submitBtn.disabled = true;
        });
    }

    function handleFileSelect(file) {
        const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
        if (!['.pdf', '.docx'].includes(ext)) {
            alert(`File format ${ext} is not supported. Please upload a PDF or DOCX resume.`);
            return;
        }

        fileName.textContent = file.name;
        fileSize.textContent = `${(file.size / 1024).toFixed(1)} KB`;

        if (ext === '.pdf') {
            fileIcon.className = "fa-solid fa-file-pdf";
        } else {
            fileIcon.className = "fa-solid fa-file-word";
        }

        dropZone.style.display = "none";
        fileInfo.style.display = "flex";
        submitBtn.disabled = false;
    }

    // Form Submission
    if (uploadForm) {
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (!fileInput.files.length) return;

            const file = fileInput.files[0];
            const formData = new FormData();
            formData.append("file", file);

            submitBtn.disabled = true;
            submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Parsing Resume...`;
            progressContainer.style.display = "block";

            // Simulated progress steps for smooth UX
            let progress = 0;
            const progressInterval = setInterval(() => {
                if (progress < 90) {
                    progress += 15;
                    progressBarFill.style.width = `${progress}%`;
                    progressPercent.textContent = `${progress}%`;
                    if (progress > 30) progressStatusText.textContent = "Extracting candidate metadata...";
                    if (progress > 60) progressStatusText.textContent = "Scanning certification credentials...";
                }
            }, 150);

            try {
                const response = await fetch("/upload-resume", {
                    method: "POST",
                    body: formData
                });

                clearInterval(progressInterval);
                const data = await response.json();

                if (response.ok && data.status === "success") {
                    progressBarFill.style.width = "100%";
                    progressPercent.textContent = "100%";
                    progressStatusText.textContent = "Parsing Complete! Redirecting...";

                    setTimeout(() => {
                        window.location.href = data.redirect_url;
                    }, 500);
                } else {
                    alert(`Upload error: ${data.detail || data.message || "Failed to parse resume."}`);
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = `<i class="fa-solid fa-magnifying-glass-arrow-right"></i> Parse & Detect Credentials`;
                    progressContainer.style.display = "none";
                }
            } catch (err) {
                clearInterval(progressInterval);
                alert(`Network error connecting to server: ${err.message}`);
                submitBtn.disabled = false;
                submitBtn.innerHTML = `<i class="fa-solid fa-magnifying-glass-arrow-right"></i> Parse & Detect Credentials`;
                progressContainer.style.display = "none";
            }
        });
    }
}

/* ==========================================================================
   2. Sample Test Data Generator / Preloader
   ========================================================================== */
async function loadSampleResume(scenario) {
    const sampleFiles = {
        'valid': 'sample_alice_johnson_valid.pdf',
        'mismatch': 'sample_bob_smith_mismatch.pdf',
        'multi': 'sample_multi_cert_resume.pdf',
        'revoked': 'sample_revoked_cert_resume.pdf'
    };

    const targetFile = sampleFiles[scenario] || 'sample_alice_johnson_valid.pdf';

    try {
        // Fetch the sample file from static/sample_data
        const fileRes = await fetch(`/static/samples/${targetFile}`);
        if (!fileRes.ok) {
            // Fallback: create mock blob directly
            createAndUploadSampleBlob(scenario);
            return;
        }

        const blob = await fileRes.blob();
        const file = new File([blob], targetFile, { type: "application/pdf" });

        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);

        const fileInput = document.getElementById("resumeFileInput");
        if (fileInput) {
            fileInput.files = dataTransfer.files;
            fileInput.dispatchEvent(new Event('change'));
        }
    } catch (e) {
        createAndUploadSampleBlob(scenario);
    }
}

async function createAndUploadSampleBlob(scenario) {
    // Generate text payload and submit directly
    const samples = {
        'valid': {
            name: "Alice Johnson",
            email: "alice.johnson@example.com",
            text: "ALICE JOHNSON\nalice.johnson@example.com | (555) 019-2834\n\nTECHNICAL SKILLS\nPython, FastAPI, Machine Learning, SQL, Docker\n\nEDUCATION\nBachelor of Science in Computer Science, Demo University\n\nCERTIFICATIONS\n- Python Programming | Certificate ID: CERT1001 | Issued by Demo Institute | Date: 2024-05-15\n"
        },
        'mismatch': {
            name: "John Doe",
            email: "john.doe@example.com",
            text: "JOHN DOE\njohn.doe@example.com | (555) 012-3456\n\nTECHNICAL SKILLS\nHTML, CSS, JavaScript, React\n\nEDUCATION\nB.Tech Information Technology\n\nCERTIFICATIONS\n- Web Development | Certificate ID: CERT1002 | Issued by Demo Institute | Date: 2024-06-20\n"
        },
        'multi': {
            name: "Alice Johnson",
            email: "alice.j@example.com",
            text: "ALICE JOHNSON\nalice.j@example.com | (555) 111-2222\n\nSKILLS\nCloud Computing, AWS, Google Cloud, Azure, Python\n\nCERTIFICATIONS\n- Python Programming | Certificate ID: CERT1001 | Demo Institute | 2024-05-15\n- AWS Certified Solutions Architect - Associate | Certificate ID: AWS-SAA-8842 | Amazon Web Services | 2024-01-18\n- Deep Learning Specialization | Certificate ID: DEEP-AI-991 | DeepLearning.AI | 2024-03-22\n- CS50: Introduction to Computer Science | Certificate ID: CS50-HARVARD-2023 | Harvard University | 2023-12-15\n"
        },
        'revoked': {
            name: "Fake Candidate",
            email: "fake@example.com",
            text: "FAKE CANDIDATE\nfake@example.com\n\nCERTIFICATIONS\n- Python Programming | Certificate ID: CERT9999 | Demo Institute | 2022-01-01\n"
        }
    };

    const s = samples[scenario] || samples['valid'];
    const blob = new Blob([s.text], { type: "text/plain" });
    const file = new File([blob], `${scenario}_resume.docx`, { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" });

    const dt = new DataTransfer();
    dt.items.add(file);
    const fileInput = document.getElementById("resumeFileInput");
    if (fileInput) {
        fileInput.files = dt.files;
        fileInput.dispatchEvent(new Event('change'));
    }
}

/* ==========================================================================
   3. Batch Verification with Progress Tracker
   ========================================================================== */
async function triggerBatchVerification(resumeId) {
    const modal = document.getElementById("verificationModal");
    if (modal) modal.style.display = "flex";

    // Advance steps sequentially
    const stepIds = ["step1", "step2", "step3", "step4", "step5", "step6", "step7", "step8"];
    let currentStep = 2;

    const interval = setInterval(() => {
        if (currentStep < stepIds.length - 1) {
            currentStep++;
            const el = document.getElementById(stepIds[currentStep]);
            if (el) {
                el.classList.add("active");
                const icon = el.querySelector(".step-circle i");
                if (icon && currentStep < 7) {
                    icon.className = "fa-solid fa-spinner fa-spin";
                }
            }
            // Mark previous as completed
            const prev = document.getElementById(stepIds[currentStep - 1]);
            if (prev) {
                const pIcon = prev.querySelector(".step-circle i");
                if (pIcon) pIcon.className = "fa-solid fa-check";
            }
        }
    }, 350);

    try {
        // First retrieve detected certificates
        const resumeRes = await fetch(`/resume/${resumeId}`);
        const resumeData = await resumeRes.json();

        const certClaims = (resumeData.certificates || []).map(c => ({
            id: c.id,
            candidate_name: resumeData.candidate_name,
            certificate_name: c.name,
            certificate_id: c.certificate_id,
            issuing_organization: c.organization,
            issue_date: c.date,
            verification_url: c.url
        }));

        // Trigger parallel verification API
        const verifyRes = await fetch("/verify-all", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                resume_id: resumeId,
                certificates: certClaims
            })
        });

        const resultData = await verifyRes.json();
        clearInterval(interval);

        // Mark all steps complete
        stepIds.forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.classList.add("active");
                const icon = el.querySelector(".step-circle i");
                if (icon) icon.className = "fa-solid fa-check";
            }
        });

        setTimeout(() => {
            window.location.href = `/results/${resumeId}`;
        }, 600);

    } catch (err) {
        clearInterval(interval);
        alert(`Verification failed: ${err.message}`);
        if (modal) modal.style.display = "none";
    }
}

/* ==========================================================================
   4. Single Certificate Verification
   ========================================================================== */
async function verifySingleCert(certId, certName, candidateName, certCode, org, date, url) {
    const cardBadge = document.getElementById(`certStatusBadge-${certId}`);
    if (cardBadge) {
        cardBadge.innerHTML = `<span class="status-pill status-pending"><i class="fa-solid fa-spinner fa-spin"></i> Checking TCP Socket...</span>`;
    }

    try {
        const response = await fetch("/verify-certificate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                id: certId,
                candidate_name: candidateName,
                certificate_name: certName,
                certificate_id: certCode,
                issuing_organization: org,
                issue_date: date,
                verification_url: url
            })
        });

        const data = await response.json();
        const status = data.status || "UNABLE_TO_VERIFY";
        const score = data.score !== undefined ? Math.round(data.score) : 0;
        const statusClass = status.toLowerCase().replace(/\s+/g, '-');

        if (cardBadge) {
            cardBadge.innerHTML = `<span class="status-pill status-${statusClass}">${status} (${score}%)</span>`;
        }
    } catch (e) {
        if (cardBadge) {
            cardBadge.innerHTML = `<span class="status-pill status-failed">ERROR: ${e.message}</span>`;
        }
    }
}
