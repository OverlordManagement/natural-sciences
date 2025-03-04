# PROGRAM TO RECORD WORDS

import pyaudio, wave, keyboard, time, math
import numpy as np
from matplotlib import pyplot as plt

def record_word_sample():

    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True  , frames_per_buffer=CHUNK)

    frames = []
    print('Press SPACE to start recording.')
    keyboard.wait('space')
    print('Recording...press SPACE to stop.')
    time.sleep(0.2)

    while True:
        try:
            data = stream.read(CHUNK)
            frames.append(data)
        except KeyboardInterrupt:
            break
        if keyboard.is_pressed('space'):
            print('Stopping recording after a brief delay...')
            time.sleep(0.2)
            break

    stream.stop_stream()
    stream.close()
    audio.terminate()

    file_name = input('Give your file a name: ').strip()
    OUTPUT_FILENAME = f'{file_name}.wav'

    wave_file = wave.open(OUTPUT_FILENAME, 'wb')
    wave_file.setnchannels(CHANNELS)
    wave_file.setsampwidth(audio.get_sample_size(FORMAT))
    wave_file.setframerate(RATE)
    wave_file.writeframes(b''.join(frames))
    wave_file.close()

def conv_bin_capac_to_dec(bit_num):
    decimal = 0
    for pwr in range(bit_num):
        decimal += 2**pwr
    return decimal

def find_max_amplitude(signal_array):

    pass

def positivify_amplitudes(signal_array):

    positivified_arr = np.array([])

    for ampl in np.nditer(signal_array):
        if ampl < 0:
            new_ampl = ampl * (-1)
            positivified_arr = np.append(positivified_arr, new_ampl)
        else:
            positivified_arr = np.append(positivified_arr, ampl)
    return positivified_arr

def find_word_stress_pattern(word_name : str, num_syllables):

    audio_file = wave.open(f'{word_name}.wav', 'rb') # opens audiofile

    sample_freq = audio_file.getframerate()
    n_samples = audio_file.getnframes()
    signal_wave = audio_file.readframes(-1) # amplitude-time data

    seconds = n_samples / sample_freq

    audio_file.close()

    signal_array = np.frombuffer(signal_wave, dtype=np.int16)
    signal_array = np.divide(signal_array, conv_bin_capac_to_dec(16)) # doesn't do anything here but may be necessary for other word inputs
    signal_array = positivify_amplitudes(signal_array) # converts negative amplitudes to positive

    times = np.linspace(0, seconds, num=n_samples)

    # PLOT TEST: plots raw audio signal
    # plt.figure(figsize=(10,5))
    # plt.plot(times, signal_array)
    # plt.title(word_name[0].upper() + word_name[1:])
    # plt.xlabel('time (s)')
    # plt.ylabel('amplitude (from -1 and 1)')
    # plt.show()

    # simplifies the wave iteratively (preserve overall trend, minimizes error from overweighted anomalous behaviour)
    # takes average of every 5 consecutive amplitude values and redefines signal_array; then takes average of every 5 of those values, etc.
    for _ in range(5):
        signal_array = sample_ampls(signal_array, 5)

    signal_array = signal_array[1:] # gets rid of the first value b/c polynomial function was sending weird values for it --- need to figure out what actually happened here

    times = np.linspace(0, seconds, num=n_samples)[::5**5][:-1][1:] # assembles array of times for the full signal function and then creates a copy with only specific
    # time-values extracted so it's still in a 1-to-1 correspondence w/ signal_array after simplification; then cuts first & last values b/c of bugs (again, actual solutions later)

    polynomial = np.polyfit(times, signal_array, len(signal_array)-1) # polynomial regression from simplified amplitude and time data; has degree 1 less than length of signal_array
    # b/c you need n+1 linear equations to find a nth-degree polynomial from input/output pairs, so this is the most precise we can go
    # actually returns an array of coefficients of the polynomial, which is why...
    polynomial = np.poly1d(polynomial) # converts to polynomial object
    # POLY1D IS DEPRECIATED: implement new model in revisions
    poly_1st_deriv = polynomial.deriv(1) # first derivative
    crit_pts_xcor = poly_1st_deriv.roots # finds x-coordinates of critical points (when 1st derivative is 0) but gives both real and complex roots
    real_crit_pts_xcor = crit_pts_xcor.real[abs(crit_pts_xcor.imag)<1e-5] # we don't care about the complex roots so we take real values
    # but poly1D approximates so can get very very tiny coefficients on i, mistakenly representing real roots as complex (which is why we put a tolerance on the coefficient of i)

    # PLOT TEST: plots the polynomial we've fitted to our data (confirms looks similar to plot of pure data)
    x = times
    y = polynomial(x)
    plt.plot(x, y)
    plt.show()

    # PLOT TEST: plots vertical lines for each critical point (confirms we're finding the right critical points)
    # for crit_pt_xcor in real_crit_pts_xcor:
    #     rx = np.array([crit_pt_xcor, crit_pt_xcor])
    #     ry = np.array([0, 0.2])
    #     plt.plot(rx, ry)
    # plt.show()

    poly_2nd_deriv = poly_1st_deriv.deriv(1) # takes 2nd derivative

    local_maxima_xcor = np.array([x for x in real_crit_pts_xcor if poly_2nd_deriv(x) < 0])[1:] # assembles list of local maxima (random slicing b/c of bug)
    local_minima_xcor = np.array([x for x in real_crit_pts_xcor if poly_2nd_deriv(x) > 0]) # ^ ^ ^ ^ minima

    # PLOT TEST: confirms we actually found the local maxima
    # for max_xcor in local_maxima_xcor:
    #     rx = np.array([max_xcor, max_xcor])
    #     ry = np.array([0, 0.2])
    #     plt.plot(rx, ry)

    local_maxima_ycor = np.array([polynomial(x) for x in local_maxima_xcor]) # assembles list of y-coordinates of maxima
    local_minima_ycor = np.array([polynomial(x) for x in local_minima_xcor])

    # create a list of maxima corresponding to the syllables
    maxima_corres_syllab_xcor = np.array([])

    for _ in range(num_syllables): # loop as many times as there are syllables
        major_maxima_ycor = local_maxima_ycor.max() # find maximum amplitude within the local amplitude maximums
        i = np.where(local_maxima_ycor == major_maxima_ycor) # find amplitude's index
        maxima_corres_syllab_xcor = np.append(maxima_corres_syllab_xcor, local_maxima_xcor[i]) # append the x-coordinate of the maximum of the maximums
        local_maxima_ycor = np.delete(local_maxima_ycor, i)
        local_maxima_xcor = np.delete(local_maxima_xcor, i)

    first_syllab_peak_t = float(maxima_corres_syllab_xcor.min())
    second_syllab_peak_t = float(maxima_corres_syllab_xcor.max())

    separator_y = np.array([polynomial(x) for x in local_minima_xcor if first_syllab_peak_t < float(x) < second_syllab_peak_t]).min()
    j = np.where(local_minima_ycor == separator_y)
    separator_t = local_minima_xcor[j]

    print(separator_t)
    print(first_syllab_peak_t, second_syllab_peak_t)

    # find when the word starts and when it stops
    bg_noise_boundary = np.poly1d(0.05 * float(signal_array.max())) # this is the y-value when the word starts and ends
    # reverse engineer from output to every t-value corresponding to bg_noise_boundary
    new_poly = polynomial - bg_noise_boundary
    t_cross_bg_noise_boundary = new_poly.roots
    t_cross_bg_noise_boundary_real = t_cross_bg_noise_boundary.real[abs(t_cross_bg_noise_boundary.imag)<1e-5]

    # PLOT TEST: make sure we're actually getting the spots where the amplitude increases beyond background noise values
    # for x in np.nditer(t_cross_bg_noise_boundary_real):
    #     xcor = [x, x]
    #     ycor = [0, 0.2]
    #     plt.plot(xcor, ycor)
    # plt.show()

    t_cross_bg_noise_boundary_real_strip_anomalies = np.array([float(t) for t in t_cross_bg_noise_boundary_real if float(t) > 0.5 and float(t) < 2.0])

    start_word_t = float(t_cross_bg_noise_boundary_real_strip_anomalies.min())
    end_word_t = float(t_cross_bg_noise_boundary_real_strip_anomalies.max())

    '''
    Whether a syllable is stressed depends on VOLUME, PITCH and DURATION:
    - the greater the volume the syllable is spoken relative to the volumes of the other syllables in the word, the higher the likelihood it's stressed
    - the higher the pitch, the greater the likelihood its stressed
    - the longer the duration, the greater the likelihood its stressed

    STEP 1: Create 3 functions:
    - cf_volumes() compares the volumes at which the syllables are spoken and outputs the one spoken more loudly
    - cf_pitch() compares the pitches at which the two syllables are spoken and outputs the one spoken in a higher pitch
    - cf_duration() compares the length of time the two syllables were spoken andoutputs the one that took longer to say
    for all 3 functions there needs to be a tolerance where if they're pretty close to eachother, it outputs that they're both the same (2nd type of output)

    STEP 2: Weigh the factors and decide which syllable is stressed and which isn't
    - if one of the syllables was the result of 2 of the functions and the other was the result of the 3rd function, 1st syllabe is stressed and second unstressed
    which means we output
    '''

    syllab_w_longer_dur = cf_duration(start_word_t, separator_t, end_word_t)
    # print(syllab_w_longer_dur)

    first_syllab_peak_ampl = polynomial(first_syllab_peak_t)
    second_syllab_peak_ampl = polynomial(second_syllab_peak_t)

    syllab_w_louder_vol = cf_volume(first_syllab_peak_ampl, second_syllab_peak_ampl)

    syllab_w_higher_pitch = cf_pitch(polynomial, start_word_t, separator_t, end_word_t)


def sample_ampls(ampl_arr, sample_size):

    simplified_ampls = np.array([])

    num_ampls_counted = 0
    sum_ampl = 0
    for a in np.nditer(ampl_arr):
        if num_ampls_counted < sample_size:
            num_ampls_counted += 1
            sum_ampl += float(a)
        else:
            avg_ampl = sum_ampl / sample_size
            simplified_ampls = np.append(simplified_ampls, avg_ampl)
            sum_ampl = float(a)
            num_ampls_counted = 1

    return simplified_ampls

def cf_duration(start_word_t, separator_t, end_word_t):
    tolerance = 0.05
    if separator_t - start_word_t > end_word_t - separator_t + tolerance:
        longer_syllab = 'first'
    elif separator_t - start_word_t < end_word_t - separator_t - tolerance:
        longer_syllab = 'second'
    else:
        longer_syllab = None
    return longer_syllab

def cf_volume(first_syllab_peak_ampl, second_syllab_peak_ampl):
    tolerance = 0.10
    if first_syllab_peak_ampl > second_syllab_peak_ampl + tolerance:
        louder_syllab = 'first'
    elif first_syllab_peak_ampl < second_syllab_peak_ampl - tolerance:
        louder_syllab = 'second'
    else:
        louder_syllab = None
    return louder_syllab

def cf_pitch(polynomial, start_word_t, separator_t, end_word_t):
    '''
    - find average slope for all the instantaneous slopes on the portion of the curve corresponding to the first syllable
    - do the same for the second syllable
    - find which is larger
    '''
    pass

find_word_stress_pattern('peanut', 2)

'''
Notes:
- selenium library for comparison w/ database (testing)
- word associations w/ adjacency lists or matrices
- beautiful soup for web scraping word concurrence frequency
'''
