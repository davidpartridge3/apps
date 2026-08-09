# Getting these onto your iPhone Home Screen

Two parts: put the files on the web (once, ~5 minutes), then add each app to your Home Screen (10 seconds each).

---

## Why this step exists

iPhone will only install something that lives at a real `https://` web address, and **only from Safari**. A downloaded file can never be added to the Home Screen, and Chrome and Edge on iPhone can't install apps at all. That's why the earlier file didn't work — nothing you did wrong.

GitHub Pages is free forever, needs no credit card, and is the least fiddly option.

---

## Part 1 — Put the files online (once)

Do this on a laptop if you have one handy; it's much easier than on a phone. Phone works too.

**1. Make a free GitHub account**
Go to **github.com** → *Sign up*. Any username is fine — it becomes part of your web address, so pick something you don't mind seeing (e.g. `davepartridge`).

**2. Create a repository**
Once signed in, tap the **+** in the top right → **New repository**.

- Repository name: `apps`
- Set it to **Public** (Pages needs this on the free plan)
- Leave everything else alone → **Create repository**

**3. Upload the folder contents**
On the new empty repo page, tap **uploading an existing file**.

Unzip `daves-apps.zip` first, then drag in **everything inside the `dist` folder** — that means `index.html`, the `workout` folder and the `kitchen` folder. Keep the folder structure; don't drag the `dist` folder itself, drag what's inside it.

Scroll down → **Commit changes**.

**4. Turn on Pages**
Go to the repo's **Settings** tab → **Pages** in the left sidebar.

- Under *Source*, choose **Deploy from a branch**
- Branch: **main**, folder: **/ (root)** → **Save**

Wait 1–2 minutes, then refresh that page. It'll show your address:

```
https://YOUR-USERNAME.github.io/apps/
```

That's your permanent link. Bookmark it.

---

## Part 2 — Add to Home Screen (per app)

Do this **in Safari**. It will not work in Chrome or Edge.

1. Open `https://YOUR-USERNAME.github.io/apps/` in **Safari**
2. Tap **Hypertrophy Hub**
3. Tap the **Share** button — the square with the arrow pointing up, at the bottom of the screen
4. Scroll down the list and tap **Add to Home Screen**
5. Tap **Add** (top right)
6. Go back and repeat steps 2–5 for **Weekly Kitchen**

You now have two app icons. They open full-screen with no browser bars, and both work **offline** after the first launch — including in the gym with no signal.

---

## Updating later

When you want new recipes or a tweak, I'll send you replacement files. Go to your repo, tap **Add file → Upload files**, drop them in, commit. The change is live in about a minute.

The apps cache themselves for offline use, so after an update: open the app, close it fully (swipe up from the app switcher), and open it again to pick up the new version.

---

## Troubleshooting

**"Add to Home Screen" isn't in the share menu** — you're not in Safari. Copy the link into Safari and try again.

**Page shows 404 right after setup** — Pages takes a minute or two to build the first time. Wait and refresh.

**The app opens in a browser tab instead of full-screen** — you tapped the bookmark rather than the Home Screen icon, or the icon was added before Pages finished. Delete the icon and re-add it.

**Nothing loads offline** — open it once with signal so it can cache itself, then it'll work offline from then on.
