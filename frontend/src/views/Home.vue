<template>
  <div class="container-fluid">
    <!-- Hero Section -->
    <div class="row align-items-center min-vh-100" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
      <div class="col-lg-6 text-white p-5">
        <h1 class="display-4 fw-bold mb-4">
          SMART PARKING SOLUTIONS for MODERN CITIES
        </h1>
        <p class="lead mb-4">
          Experience hassle-free parking with our advanced vehicle parking management system. 
          Reserve spots, track your parking sessions, and enjoy seamless parking experiences.
        </p>
        <div class="d-flex gap-3">
          <router-link to="/register" class="btn btn-light btn-lg px-4">
            <i class="bi bi-person-plus"></i> Get Started
          </router-link>
          <router-link to="/login" class="btn btn-outline-light btn-lg px-4">
            <i class="bi bi-box-arrow-in-right"></i> Login
          </router-link>
        </div>
      </div>
      <div class="col-lg-6 p-5">
        <div class="text-center">
          <i class="bi bi-car-front" style="font-size: 15rem; color: rgba(255,255,255,0.3);"></i>
        </div>
      </div>
    </div>

    <!-- Features Section -->
    <div class="row py-5 bg-light">
      <div class="col-12 text-center mb-5">
        <h2 class="display-5 fw-bold">Why Choose Our Parking System?</h2>
        <p class="lead text-muted">Advanced features designed for modern parking needs</p>
      </div>
      
      <div class="col-lg-4 col-md-6 mb-4">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center p-4">
            <div class="mb-3">
              <i class="bi bi-clock text-primary" style="font-size: 3rem;"></i>
            </div>
            <h5 class="card-title">Real-time Availability</h5>
            <p class="card-text">Check parking spot availability in real-time and reserve your spot instantly.</p>
          </div>
        </div>
      </div>
      
      <div class="col-lg-4 col-md-6 mb-4">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center p-4">
            <div class="mb-3">
              <i class="bi bi-credit-card text-primary" style="font-size: 3rem;"></i>
            </div>
            <h5 class="card-title">Automatic Billing</h5>
            <p class="card-text">Pay only for the time you use with our automatic billing system.</p>
          </div>
        </div>
      </div>
      
      <div class="col-lg-4 col-md-6 mb-4">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center p-4">
            <div class="mb-3">
              <i class="bi bi-shield-check text-primary" style="font-size: 3rem;"></i>
            </div>
            <h5 class="card-title">Secure & Reliable</h5>
            <p class="card-text">Your vehicle is safe with our secure parking management system.</p>
          </div>
        </div>
      </div>
      
      <div class="col-lg-4 col-md-6 mb-4">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center p-4">
            <div class="mb-3">
              <i class="bi bi-graph-up text-primary" style="font-size: 3rem;"></i>
            </div>
            <h5 class="card-title">Analytics & Reports</h5>
            <p class="card-text">Track your parking history and get detailed reports and analytics.</p>
          </div>
        </div>
      </div>
      
      <div class="col-lg-4 col-md-6 mb-4">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center p-4">
            <div class="mb-3">
              <i class="bi bi-phone text-primary" style="font-size: 3rem;"></i>
            </div>
            <h5 class="card-title">Mobile Friendly</h5>
            <p class="card-text">Access the parking system from any device with our responsive design.</p>
          </div>
        </div>
      </div>
      
      <div class="col-lg-4 col-md-6 mb-4">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center p-4">
            <div class="mb-3">
              <i class="bi bi-headset text-primary" style="font-size: 3rem;"></i>
            </div>
            <h5 class="card-title">24/7 Support</h5>
            <p class="card-text">Get help anytime with our round-the-clock customer support.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- How It Works Section -->
    <div class="row py-5">
      <div class="col-12 text-center mb-5">
        <h2 class="display-5 fw-bold">How It Works</h2>
        <p class="lead text-muted">Simple steps to start parking smart</p>
      </div>
      
      <div class="col-lg-3 col-md-6 text-center mb-4">
        <div class="position-relative">
          <div class="bg-primary text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 80px; height: 80px;">
            <span class="h4 mb-0">1</span>
          </div>
          <h5>Register</h5>
          <p class="text-muted">Create your account in minutes</p>
        </div>
      </div>
      
      <div class="col-lg-3 col-md-6 text-center mb-4">
        <div class="position-relative">
          <div class="bg-primary text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 80px; height: 80px;">
            <span class="h4 mb-0">2</span>
          </div>
          <h5>Find Spot</h5>
          <p class="text-muted">Browse available parking lots</p>
        </div>
      </div>
      
      <div class="col-lg-3 col-md-6 text-center mb-4">
        <div class="position-relative">
          <div class="bg-primary text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 80px; height: 80px;">
            <span class="h4 mb-0">3</span>
          </div>
          <h5>Reserve</h5>
          <p class="text-muted">Reserve your parking spot</p>
        </div>
      </div>
      
      <div class="col-lg-3 col-md-6 text-center mb-4">
        <div class="position-relative">
          <div class="bg-primary text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 80px; height: 80px;">
            <span class="h4 mb-0">4</span>
          </div>
          <h5>Park & Pay</h5>
          <p class="text-muted">Park safely and pay automatically</p>
        </div>
      </div>
    </div>

    <!-- CTA Section -->
    <div class="row py-5" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
      <div class="col-12 text-center text-white">
        <h2 class="display-5 fw-bold mb-4">Ready to Start?</h2>
        <p class="lead mb-4">Join thousands of users who trust our parking system</p>
        <router-link to="/register" class="btn btn-light btn-lg px-5">
          <i class="bi bi-person-plus"></i> Create Account Now
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home'
}
</script> 