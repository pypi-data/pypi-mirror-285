package com.maltaisn.notes;


import static androidx.test.espresso.Espresso.onView;
import static androidx.test.espresso.action.ViewActions.click;
import static androidx.test.espresso.action.ViewActions.replaceText;
import static androidx.test.espresso.assertion.ViewAssertions.matches;
import static androidx.test.espresso.matcher.ViewMatchers.isDisplayed;
import static androidx.test.espresso.matcher.ViewMatchers.withContentDescription;
import static androidx.test.espresso.matcher.ViewMatchers.withId;
import static androidx.test.espresso.matcher.ViewMatchers.withParent;
import static androidx.test.espresso.matcher.ViewMatchers.withText;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.containsString;

import android.view.View;
import android.view.ViewGroup;
import android.view.ViewParent;

import androidx.test.ext.junit.rules.ActivityScenarioRule;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.filters.LargeTest;

import com.maltaisn.notes.R;
import com.maltaisn.notes.ui.main.MainActivity;

import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;
import org.junit.After;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;

@RunWith(AndroidJUnit4.class)
public class SetLeftSwipeToDelete {

    @Rule
    public ActivityScenarioRule<MainActivity> mActivityScenarioRule =
            new ActivityScenarioRule<>(MainActivity.class);

    @Test
    public void setLeftSwipeToDelete() {
        ViewInteraction _1 = onView(allOf(withContentDescription("Open drawer"),
                isDisplayed()));
        _1.perform(click());
        ViewInteraction _2 = onView(allOf(withText("Settings"),
                isDisplayed()));
        _2.perform(click());
        ViewInteraction _3 = onView(allOf(withText(containsString("Swipe left")),
                isDisplayed()));
        _3.perform(click());
        ViewInteraction _4 = onView(allOf(withId(android.R.id.text1), withText("Delete"), isDisplayed()));
        _4.perform(click());

        ViewInteraction _5 = onView(allOf(withId(android.R.id.summary),
                withText("Delete")));
        _5.check(matches(isDisplayed()));
    }
}
